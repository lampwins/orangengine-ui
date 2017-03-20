(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices', [
    'satellizer',
    'BlurAdmin.pages.devices.form'
    ]).config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devcies', {
          url: '/devcies',
          title: 'Devcies',
          templateUrl: 'app/pages/devices/devices.html',
          sidebarMeta: {
            icon: 'ion-fireball',
            order: 1,
          },
        });
  }

})();