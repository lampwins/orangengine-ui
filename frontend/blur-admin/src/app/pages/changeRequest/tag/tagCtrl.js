(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.tag')
      .controller('TagCtrl', TagCtrl);

  /** @ngInject */
  function TagCtrl($scope) {

    $scope.policy = {
        option: 'one'
      };

    $scope.append = {
      option: 'one'
    };


  }
})();
