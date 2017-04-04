
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest', ['satellizer'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('changeRequest', {
          url: '/changeRequest',
          templateUrl: 'app/pages/changeRequest/changeRequest.html',
          title: 'Change Request',
          sidebarMeta: {
            icon: 'ion-android-home',
            order: 0,
          },
        });
  }

})();
