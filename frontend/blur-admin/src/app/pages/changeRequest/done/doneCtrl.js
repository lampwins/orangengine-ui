(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.done')
      .controller('DoneCtrl', DoneCtrl);

  /** @ngInject */
  function DoneCtrl($scope, $location) {

    $scope.go = function(path) {
      $location.path(path);
    };


  }
})();
