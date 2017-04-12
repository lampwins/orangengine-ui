/**
 * @author v.lugovksy
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.dashboard')
      .controller('DashboardQueueCtrl', DashboardQueueCtrl);


  /** @ngInject */
  function DashboardQueueCtrl($scope, baConfig, $http, $auth, $location, $uibModal, $uibModalStack, $timeout) {

    var vm = this;
    vm.queueData = [];

    $http({
      method : "GET",
      url : "/api/v1.0/change_requests/?status=open"
    }).then(function mySuccess(response){
      console.log(response)
      var elements = response.data.data;
      elements.forEach(function(e){
        vm.queueData.push(e);
      }, this);
      console.log(vm.queueData);
    }, function myError(response) {
      console.log(response)
    });

    vm.go = function(id) {
      $location.path('/changeRequest/' + id + '/summary');
    };

    vm.cancel = function(id) {
      $scope.changeRequestCancelId = id;
      $uibModal.open({
        animation: true,
        templateUrl: 'app/pages/dashboard/DashboardQueue/cancelConfirmModal.html',
        size: 'sm',
        scope: $scope
      });
    }

    vm.cancelConfirm = function(id) {
      console.log(id);
      $http({
        method : "PATCH",
        url : "/api/v1.0/change_requests/" + id + "/",
        data: {
          status: "canceled"
        }
      }).then(function mySuccess(response){
        console.log(response)
        $uibModalStack.dismissAll();
        var index = vm.queueData.findIndex(item => item.id === id);
        vm.queueData.splice(index, 1);
        console.log(vm.queueData);
      }, function myError(response) {
        console.log(response)
      });
    }


}
})();
