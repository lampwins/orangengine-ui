(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest.confirm')
      .controller('ConfirmCtrl', ConfirmCtrl);

  /** @ngInject */
  function ConfirmCtrl($scope) {

    $scope.checkboxModel = {
       commit : true
     };


  }
})();
