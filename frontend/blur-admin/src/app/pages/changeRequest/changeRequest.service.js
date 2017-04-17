
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.changeRequest')
      .service('changeRequestService', changeRequestService);

  /** @ngInject */
  function changeRequestService() {

    var _changeRequestIdStore, _get;

    _changeRequestIdStore = {};

    _get = function(id) {
      return _changeRequestIdStore[id];
    }




    return {
      get: _get,
    }

  }

})();
