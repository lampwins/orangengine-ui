(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.form', ['satellizer', 'ui.select', 'ngSanitize'])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('changeRequest.form', {
          url: '/form',
          title: 'New Device',
          templateUrl: 'app/pages/changeRequest/form/form.html',
        });
  }

})();