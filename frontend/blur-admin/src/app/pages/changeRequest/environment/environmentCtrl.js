(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.environment')
      .controller('EnvironmentCtrl', EnvironmentCtrl);

  /** @ngInject */
  function EnvironmentCtrl($scope) {

    var vm = this;
    vm.disabled = undefined;

    vm.deviceTypeSelectItems = [
      {label: 'Juniper SRX', value: 'juniper_srx'},
      {label: 'Palo Alto Panorama', value: 'palo_alto_panorama'},
    ];



  }
})();
