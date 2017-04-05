(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.locations')
    .controller('LocationsCtrl', LocationsCtrl)

  /** @ngInject */
  function LocationsCtrl($scope, $http, $timeout) {

    var vm = this;
    vm.sharedData = [];

    vm.newLocationName = '';

    vm.updateList = function() {
      $http({
        method: 'GET',
        url: '/api/v1.0/locations/'
      }).then(function successCallback(response) {
          console.log(response)
          vm.sharedData["locations"] = response.data.data;
        }, function errorCallback(response) {
          console.log(response)
        }
      );
    }

    vm.updateList();

    vm.submitNew = function() {
      if(vm.newLocationName){
        $http({
          method: 'POST',
          url: '/api/v1.0/locations/',
          data: {name: this.newLocationName}
        }).then(function successCallback(response) {
            console.log(response)
            vm.newLocationName = '';
            vm.updateList();
          }, function errorCallback(response) {
            console.log(response)
          }
        );
      }
    }

  };

})();