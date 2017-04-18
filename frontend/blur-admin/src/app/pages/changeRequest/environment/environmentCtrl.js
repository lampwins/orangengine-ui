(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.environment')
      .controller('EnvironmentCtrl', EnvironmentCtrl);

  /** @ngInject */
  function EnvironmentCtrl($scope, $http) {

    var vm = this;
    vm.disabled = undefined;

    vm.deviceTypeSelectItems = [
      {label: 'Juniper SRX', value: 'juniper_srx'},
      {label: 'Palo Alto Panorama', value: 'palo_alto_panorama'},
    ];

    $http({
      method : "GET",
      url : "/api/v1.0/change_requests/"
    }).then(function mySuccess(response){
      console.log(response)
      $scope.environmentData = response.data.data;
    }, function myError(response) {
      console.log(response)
      $scope.name = response.statusText;
    });



  }
})();
