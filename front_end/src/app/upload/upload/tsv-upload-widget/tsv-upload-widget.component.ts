import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { UploadService } from 'src/app/shared/services/upload.service';
import { Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner'; 

@Component({
  selector: 'app-tsv-upload-widget',
  templateUrl: './tsv-upload-widget.component.html',
  styleUrls: ['./tsv-upload-widget.component.css']
})
export class TSVUploadWidgetComponent implements OnInit {

  constructor(
    private uploadService: UploadService,
    private router: Router,
    private spinner: NgxSpinnerService
  ) { }

  fileTypeError = false;
  uploadError = false;
  file: File = null;
  fileSize: string;
  readyToUpload = false;
  loading = false;

  ngOnInit(): void {
  }

  handleFileInput(files: FileList) {
    this.fileTypeError = false;
    this.uploadError = false;

    this.file = files.item(0);
    if (this.file?.type !== 'text/csv') {
      this.fileTypeError = true;
    } else {
      this.calculateFileSize();
      this.readyToUpload = true;
    }
  }

  handleFileInputFromBrowse(event) {
    this.fileTypeError = false;
    this.uploadError = false;

    this.file = event.target?.files?.item(0)
    if (this.file?.type !== 'text/csv') {
      this.fileTypeError = true;
    } else {
      this.calculateFileSize();
      this.readyToUpload = true;
    }
  }

  clearFile() {
    this.file = null;
    this.readyToUpload = false;
    this.fileTypeError = false;
    this.uploadError = false;
  }

  calculateFileSize() {
    if (this.file.size > 1000000) {
      this.fileSize = `${this.file.size / 1000000} MB`;
    } else {
      this.fileSize = `${this.file.size / 1000} KB`;
    }
  }

  uploadCSV() {
    this.uploadService.clearCache();
    this.spinner.show('uploading-csv');
    this.loading = true;
    this.uploadService.uploadCSV(this.file)
      .then(data => {
        // navigate to create step
        this.spinner.hide('uploading-csv');
        this.loading = false;
        this.router.navigate(['/upload/validate'], {queryParams: {'csvUpload': 'true'}});
      })
      .catch(error => {
        this.fileTypeError = true;
      });
  }
}
