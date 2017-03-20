(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.form', ['satellizer', 'ui.select', 'ngSanitize'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devices.form', {
          url: '/form',
          title: 'Devcies',
          templateUrl: 'app/pages/devices/devicesForm/devicesForm.html',
        });
  }

})();