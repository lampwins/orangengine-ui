
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest')
      .service('changeRequestService', changeRequestService);

  /** @ngInject */
  function changeRequestService($http, $location, $q) {

    var _changeRequest, _get, _changeRequestId, _scoreObject;

    this.updateId = function(id) {
      _changeRequestId = id;
    };

    this.getChangeRequest = function() {
      if (_changeRequestId !== undefined) {
        return $http({
          method : "GET",
          url : "/api/v1.0/change_requests/" + _changeRequestId + "/?status=open"
        }).then(function mySuccess(response){
          console.log(response);
          if (response.data.data.status != 'open') {
            $location.path("/dashboard")
          }else{
            _changeRequest = response.data.data;
            return _changeRequest;
          }
        }, function myError(response) {
          console.log(response)
          $location.path("/dashboard")
        });
      } else {
        return $q.resolve(_changeRequest);
      }
    };

    this.getScore = function() {
      if (_changeRequestId !== undefined) {
        return $http({
            method : "GET",
            url : "/api/v1.0/oe/change_request/" + _changeRequestId + "/score/"
          }).then(function mySuccess(response){
            console.log(response);
            _scoreObject = response.data.data;
            return _scoreObject;
          }, function myError(response) {
            console.log(response)
            $location.path("/dashboard")
          });
      }
    };

  }

})();
