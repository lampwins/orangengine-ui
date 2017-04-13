(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.summary')
      .controller('SummaryCtrl', SummaryCtrl);

  /** @ngInject */
  function SummaryCtrl($scope, $location) {

    console.log("hello");

    $scope.go = function(path) {
      $location.path(path);
    };

  }
})();
