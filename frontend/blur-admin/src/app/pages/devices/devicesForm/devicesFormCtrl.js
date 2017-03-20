(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.form')
    .controller('DevicesFormCtrl', DevicesFormCtrl)

  /** @ngInject */
  function DevicesFormCtrl($scope) {

    var vm = this;

    vm.deviceInfo = {};

    vm.deviceTypeSelectItems = [
      {label: 'Juniper SRX', value: 'juniper_srx'},
      {label: 'Palo Alto Panorama', value: 'palo_alto_panorama'},
    ];

  };

})();