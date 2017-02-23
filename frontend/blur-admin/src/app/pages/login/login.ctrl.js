(function () {
  'use strict';

  angular.module('BlurAdmin.pages.login')
    .controller('loginCtrl', function($scope, $auth, $rootScope, $window, $location, $httpParamSerializerJQLike) {

      $scope.login = function() {

      var user = {
        email: $scope.email,
        password: $scope.password
      };

      var requestConfig = {
        url: "/api/auth/login",
        headers: {'Content-Type': 'application/json'},
        data: $httpParamSerializerJQLike(user),
      };

      console.log($scope)

      $auth.login(user, requestConfig)
        .then(function(response) {
          console.log(response);
          $window.localStorage.currentUserToken = JSON.stringify(response.data.auth_token);
          $rootScope.currentUser = JSON.parse(localStorage.getItem('currentUserToken'));
          $location.path('/dashboard');
        })
        .catch(function(response) {
          console.log(response);
        });
    };

  });

})();