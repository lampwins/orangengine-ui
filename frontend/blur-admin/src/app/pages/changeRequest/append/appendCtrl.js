(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.append')
      .controller('AppendCtrl', AppendCtrl);

  /** @ngInject */
  function AppendCtrl($scope) {

    $scope.policy = {
        option: 'one'
      };

    $scope.append = {
      option: 'one'
    };


  }
})();
