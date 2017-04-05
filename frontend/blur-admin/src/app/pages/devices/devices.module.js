(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices', [
    'satellizer',
    'BlurAdmin.pages.devices.form',
    'BlurAdmin.pages.devices.list',
    'BlurAdmin.pages.devices.locations'
    ]).config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devices', {
          url: '/devices',
          template : '<ui-view  autoscroll="true" autoscroll-body-top></ui-view>',
          abstract: true,
          title: 'Devices',
          sidebarMeta: {
            icon: 'ion-fireball',
            order: 1,
          },
        });
  }

})();