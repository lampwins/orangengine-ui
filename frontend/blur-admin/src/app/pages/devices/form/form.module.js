(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.form', ['satellizer', 'ui.select', 'ngSanitize'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devices.form', {
          url: '/form',
          title: 'New Device',
          templateUrl: 'app/pages/devices/form/form.html',
          sidebarMeta: {
            icon: 'ion-ios-location',
            order: 2,
          },
        });
  }

})();