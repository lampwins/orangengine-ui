(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.locations', ['satellizer', 'ngSanitize'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devices.locations', {
          url: '/locations',
          title: 'Locations',
          templateUrl: 'app/pages/devices/locations/locations.html',
          sidebarMeta: {
            icon: 'ion-ios-location',
            order: 0,
          },
          controller: 'LocationsCtrl'
        });
  }

})();