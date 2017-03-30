(function () {
  'use strict';

  angular.module('BlurAdmin.pages.devices.list', ['satellizer', 'ui.select', 'ngSanitize'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('devices.list', {
          url: '/list',
          title: 'Devices',
          templateUrl: 'app/pages/devices/list/list.html',
          //sidebarMeta: {
          //  icon: 'ion-fireball',
          //  order: 1,
          //},
          controller: 'DevicesListCtrl'
        });
  }

})();