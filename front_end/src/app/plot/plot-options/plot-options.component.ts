import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { PlotService } from '../../shared/services/plot.service';
import { ObjectMetadata, DimensionContext } from '../../shared/models/object-metadata';
import { QueryBuilderService } from '../../shared/services/query-builder.service';
import { PlotlyConfig, AxisBlock } from 'src/app/shared/models/plotly-config';
import { MapBuilder } from 'src/app/shared/models/map-builder';
import { PlotlyBuilder, AxisOption, Axis, Constraint } from 'src/app/shared/models/plotly-builder';
import { Response } from 'src/app/shared/models/response';
import { PlotValidatorService as validator } from 'src/app/shared/services/plot-validator.service';
import { NgxSpinnerService } from 'ngx-spinner';
import { environment } from 'src/environments/environment';
@Component({
  selector: 'app-plot-options',
  templateUrl: './plot-options.component.html',
  styleUrls: ['./plot-options.component.css'],
})
export class PlotOptionsComponent implements OnInit {

  public metadata: ObjectMetadata;
  public allPlotTypeData: PlotlyConfig[];
  public plotTypeData: PlotlyConfig[]; // plotTypeData displayed depending on dimensionality
  public selectedPlotType: PlotlyConfig;
  public objectId: string;
  private tempObjectId: string; // temporary object ID for bricks with extended properties to include lat long
  public coreTypePlot = false;
  public numberOfAxes = 2; // currently just for core types
  private coreTypeName: string;
  public isMap = false; // determines if we should use UI for map config
  public mapBuilder: MapBuilder;
  public requiresMergeForMapping = false;
  public axisOptions: AxisOption[]; // user facing options that displays options based on what can be plotted
  private _axisOptions: AxisOption[]; // stores all axis options regardless of if theyre allowed to be displayed
  public plot: PlotlyBuilder;
  public needsConstraints = false;
  public unableToPlot = false;
  constrainableDimensions: DimensionContext[];
  public invalid = false;
  public tooManyTraces = false;
  public plotTooLarge = false;
  public loading = true;
  private previousUrl: string;

  constructor(
    private route: ActivatedRoute,
    private plotService: PlotService,
    private queryBuilder: QueryBuilderService,
    private router: Router,
    private spinner: NgxSpinnerService,
    ) { }

  ngOnInit() {
    this.spinner.show();

    this.previousUrl = this.queryBuilder.getPreviousUrl();

    // get object id
    this.route.params.subscribe(params => {
        if (params['id']) {
          this.objectId = params.id;
          this.plot = this.plotService.getPlotlyBuilder();
          this.plot.object_id = params.id;
        }
    });

    this.route.queryParams.subscribe(queryParams => {
      if (queryParams['coreType']) {
        this.coreTypePlot = true;
        this.coreTypeName = queryParams['coreType'];
        const query = JSON.parse(localStorage.getItem('coreTypePlotParams'));
        this.plot = this.plotService.getPlotlyBuilder(true, query);
        this.plot.title = this.coreTypeName;
      }
    });

    const mapBuilder = JSON.parse(localStorage.getItem('mapBuilder'));
    if (mapBuilder) {
      if (!mapBuilder.tempObjectId) {
        this.mapBuilder = Object.assign(new MapBuilder(this.coreTypePlot),mapBuilder);
      } else {
        // clear the plot options if theres a temp object id to load regular brick
        delete this.plot.plot_type;
      }
    }
    if (this.mapBuilder) {
      this.isMap = true;
    }

    if (this.coreTypePlot) {
      this.queryBuilder.getCoreTypeProps(this.coreTypeName)
        .subscribe((data: Response<AxisOption>) => {
          this.axisOptions = data.results;
          this._axisOptions = [...this.axisOptions];
          this.getPlotTypes();
          // this.loading = false;
          this.spinner.hide();
        });
    } else {
      // get metadata and assign to AxisOption type 
      // TODO: needs to be formatted like this on the backend
      this.plotService.getObjectPlotMetadata(this.objectId)
        .subscribe(({result, axisOptions}: {result: ObjectMetadata, axisOptions: AxisOption[]}) => {
          this.loading = false;
          this.spinner.hide();
          this.metadata = result;

          // as of now we are not supporting plotting brick with non numeric data vars
          const numericDataVars = axisOptions
            .filter(axisOption => axisOption.data_variable !== undefined)
            .reduce((acc, axisOption) => acc || validator.isNumeric(axisOption), false);

          if (!numericDataVars) {
            this.unableToPlot = true;
            return;
          }

          this.plot.title = this.metadata.data_type.oterm_name + ` (${this.objectId})`;
          if (!validator.validPlot(this.plot)) {
            this.setConstrainableDimensions();
          }
          this.axisOptions = axisOptions;
          this._axisOptions = [...this.axisOptions];

          if (this.axisOptions.filter(x => x.data_variable !== undefined).length > 1) {
            this.plot.multi_data_vars = true;
          }

          this.getPlotTypes();
          if (this.mapBuilder && this.mapBuilder.dimWithCoords === undefined) {
            this.mapBuilder.setLatLongDimension(this.axisOptions);
          }

          // check if brick has lat and long data in its dimensions for UI notification
          this.requiresMergeForMapping = !validator.hasCoordsInDimensions(this.metadata);
        });
    }
  }

  getPlotTypes() {
    // TODO: add map types but figure out a way to only show it if theres lat and long
    this.plotService.getPlotTypes()
      .subscribe((data: Response<PlotlyConfig>) => {

        // add map option to plots if the variables include lat and long
        // TODO: use results from JSON connect_to_properties method
        let includeMap = this.axisOptions
        .filter(option => {
          return option.name.toLowerCase() === 'latitude' || option.name.toLowerCase() === 'longitude'
        }).length === 2;

        // items are mappable if they can be connected to an upstream item with lat long data
        if (this.metadata.connects_to_properties.value) {
          includeMap = true;
        }

        if (!this.coreTypePlot) {
          this.plotTypeData = validator.getValidPlotTypes(data.results, this.axisOptions, includeMap, this.metadata.dim_context.length);
        } else {
          // dont show map options if there is no google maps api key in env
          this.plotTypeData = includeMap && environment.GOOGLE_MAPS_API_KEY.length
            ? data.results
            : data.results.filter(result => !result.map && result.name !== 'Heatmap');
        }
        // this should never be true for core types
        if (this.plotTypeData.length === 0) {
          this.unableToPlot = true;
        }

        if (this.isMap) {
          this.plot.plot_type = this.plotTypeData[0];
        }
    });
  }

  updatePlotType(event: PlotlyConfig) {
    this.invalid = false; // dont mark all the other forms invalid before anyone tried to fill them out
    this.isMap = false;
    this.plot.plot_type = event;
    if (event.map) {
      this.isMap = true;
      this.mapBuilder = new MapBuilder(this.coreTypePlot);
      if (this.coreTypePlot) {
        this.mapBuilder.query = this.plot.query;
      } else {
        if (this.requiresMergeForMapping) {
          // brick needs to merge with upstream data to get coordinates; get temporary extended brick
          this.loading = true;
          this.spinner.show();
          this.plotService.getMergedBrickWithCoords(this.objectId)
            .subscribe(({tempId, metadata, axisOptions}) => {
              this.metadata = metadata;
              this._axisOptions = [...axisOptions];
              this.axisOptions = [...axisOptions];
              this.loading = false;
              this.mapBuilder.setLatLongDimension(this._axisOptions);
              this.mapBuilder.tempObjectId = tempId;
              this.mapBuilder.brickId = this.objectId;
              this.spinner.hide();
            })
        } else {
          // brick has coords without needing to be merged; can use same brick
          this.mapBuilder.brickId = this.objectId;
          this.mapBuilder.setLatLongDimension(this._axisOptions);
        }
      }
    } else {
      delete this.mapBuilder;
      localStorage.removeItem('mapBuilder');
    }
    if (event.axis_data.z) {
      this.plot.axes.z = new Axis();
    } else {
      // set data vars to be plotted on y axis instead of z axis
      if (this.plot.axes?.z) {
        this.plot.axes.y = this.plot.axes.z;
        this.setConstrainableDimensions();
        delete this.plot.axes.z;
      }
    }
    if (!this.coreTypePlot && !validator.validPlot(this.plot)) {
      this.setConstrainableDimensions();
    }
  }

  handleSelectedAxis(event: AxisOption) {
    if (this.coreTypePlot) {
      this.axisOptions = [...this.axisOptions.filter(option => option.term_id !== event.term_id)];
    } else {
      this.axisOptions = [...this.axisOptions.filter(option => {
        if (validator.hasOneRemainingAxis(this.plot) && !validator.hasDataVarsInPlot(this.plot)) {
          return option.data_variable !== event.data_variable && option.dimension === undefined;
        }
        return option.dimension !== event.dimension || option.data_variable !== event.data_variable;
      })];
      this.setConstrainableDimensions();
    }
  }

  handleSelectionCleared() {
    if (this.coreTypePlot) {
      this.axisOptions = [
        ...this._axisOptions.filter((option) => {
          for (const [_, val] of Object.entries(this.plot.axes)) {
            if (val.data?.term_id === option.term_id) {
              return false;
            }
          }
          return true;
        })
      ]
    } else {
      this.axisOptions = [
        ...this._axisOptions.filter((option) => {
          for (const [_, val] of Object.entries(this.plot.axes)) {
            if (validator.hasOneRemainingAxis(this.plot) && option.dimension !== undefined) {
              // only show data variables if theres one axis left and no data vars have been chosen yet
              return validator.hasDataVarsInPlot(this.plot);
            }
            if (val.data_var_idx !== undefined && val.data_var_idx === option.dimension_variable) { return false; }
            if (val.dim_idx !== undefined && val.dim_idx === option.dimension) { return false; }
          }
          return true;
        })
      ];
      this.setConstrainableDimensions();
    }
  }

  setConstrainableDimensions() {
    // whichever dimensions arent selected are all displayed as constrainable items
    this.constrainableDimensions = [
      ...this.metadata.dim_context.filter((dim, idx) => {
        return this.plot.axes.x.dim_idx !== idx &&
        this.plot.axes.y.dim_idx !== idx &&
        this.plot.axes.z?.dim_idx !== idx;
      })
    ];
    this.plot.setDimensionConstraints(this.constrainableDimensions, this.metadata);
  }

  shouldHideSeries() {
    // determines whether series should be an option for plot constraint
    return this.plot.plot_type?.name.toLowerCase().includes('heatmap')
  }

  submitPlot() {
    if (this.isMap) {
      localStorage.setItem('mapBuilder', JSON.stringify(this.mapBuilder));
      this.router.navigate(['/plot/map/result']);
      return;
    }

    if (!validator.validPlot(this.plot)) {
      this.invalid = true;
      return;
    }

    const [tooManyTraces, requiresGL] = validator.validateSize(this.plot, this.metadata);

    if (tooManyTraces) {
      this.tooManyTraces = true;
      return;
    }

    if (requiresGL) {
      // TODO: see if there is a way to use WebGL for different types of plots
      this.plotTooLarge = true;
      return;
    }

    localStorage.setItem('plotlyBuilder', JSON.stringify(this.plot));
    if (this.coreTypePlot) {
      this.router.navigate(['/plot/result'], {queryParams: {
        coreType: this.coreTypeName,
      }});
    } else {
      this.router.navigate([`plot/result/${this.objectId}`]);
    } 
  }

  get hasAxisOptions() {
    return this._axisOptions?.length > 0;
  }
  

  onGoBack(id) {
  if (this.previousUrl) {
    this.router.navigate([this.previousUrl]);
  } else {
    this.router.navigate(['/search/result'])
  }
  }

}
