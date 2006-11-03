/*
 * Copyright 2006 SitePoint Pty. Ltd, www.sitepoint.com
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *   http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS;
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

function Ajax() {
  this.req = null;
  this.url = null;
  this.status = null;
  this.statusText = '';
  this.method = 'GET';
  this.async = true;
  this.dataPayload = null;
  this.readyState = null;
  this.responseText = null;
  this.responseXML = null;
  this.handleResp = null;
  this.responseFormat = 'text', // 'text', 'xml', 'object'
  this.mimeType = null;
  this.headers = [];

  
  this.init = function() {
    var i = 0;
    var reqTry = [ 
      function() { return new XMLHttpRequest(); },
      function() { return new ActiveXObject('Msxml2.XMLHTTP') },
      function() { return new ActiveXObject('Microsoft.XMLHTTP' )} ];
      
    while (!this.req && (i < reqTry.length)) {
      try { 
        this.req = reqTry[i++]();
      } 
      catch(e) {}
    }
    return true;
  };
  this.doGet = function(url, hand, format) {
    this.url = url;
    this.handleResp = hand;
    this.responseFormat = format || 'text';
    this.doReq();
  };
  this.doPost = function(url, dataPayload, hand, format) {
    this.url = url;
    this.dataPayload = dataPayload;
    this.handleResp = hand;
    this.responseFormat = format || 'text';
    this.method = 'POST';
    this.doReq();
  };
  this.doReq = function() {
    var self = null;
    var req = null;
    var headArr = [];
    
    if (!this.init()) {
      alert('Could not create XMLHttpRequest object.');
      return;
    }
    req = this.req;
    req.open(this.method, this.url, this.async);
    if (this.method == "POST") {
      this.req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    }
    if (this.method == 'POST') {
      req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    }
    self = this;
    req.onreadystatechange = function() {
      var resp = null;
      self.readyState = req.readyState;
      if (req.readyState == 4) {
        
        self.status = req.status;
        self.statusText = req.statusText;
        self.responseText = req.responseText;
        self.responseXML = req.responseXML;
        
        switch(self.responseFormat) {
          case 'text':
            resp = self.responseText;
            break;
          case 'xml':
            resp = self.responseXML;
            break;
          case 'object':
            resp = req;
            break;
        }
        
        if (self.status > 199 && self.status < 300) {
          if (!self.handleResp) {
            alert('No response handler defined ' +
              'for this XMLHttpRequest object.');
            return;
          }
          else {
            self.handleResp(resp);
          }
        }
        
        else {
          self.handleErr(resp);
        }
      }
    }
    req.send(this.dataPayload);
  };
  this.abort = function() {
    if (this.req) {
      this.req.onreadystatechange = function() { };
      this.req.abort();
      this.req = null;
    }
  };
  this.handleErr = function() {
    var errorWin;
    // Create new window and display error
    try {
      errorWin = window.open('', 'errorWin');
      errorWin.document.body.innerHTML = this.responseText;
    }
    // If pop-up gets blocked, inform user
    catch(e) {
      alert('An error occurred, but the error message cannot be' +
      ' displayed because of your browser\'s pop-up blocker.\n' +
      'Please allow pop-ups from this Web site.');
    }
  };
  this.setMimeType = function(mimeType) {
    this.mimeType = mimeType;
  };
  this.setHandlerResp = function(funcRef) {
    this.handleResp = funcRef;
  };
  this.setHandlerErr = function(funcRef) {
    this.handleErr = funcRef; 
  };
  this.setHandlerBoth = function(funcRef) {
    this.handleResp = funcRef;
    this.handleErr = funcRef;
  };
  this.setRequestHeader = function(headerName, headerValue) {
    this.headers.push(headerName + ': ' + headerValue);
  };
  
}
