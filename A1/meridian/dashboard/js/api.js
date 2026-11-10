/* api.js - thin wrapper over the service layer.
 * 2016. The base URL is set at deploy time by a sed in the release
 * script, which is why it looks like this.
 */
var MeridianApi = (function ($) {
    var BASE = window.MERIDIAN_API_BASE || 'http://localhost:8081';

    function get(path, params, cb) {
        $.ajax({
            url: BASE + path,
            data: params || {},
            dataType: 'json',
            success: function (data) { cb(null, data); },
            error: function (xhr, status) { cb(status || 'error', null); }
        });
    }

    return {
        health:    function (cb) { get('/api/health', null, cb); },
        stations:  function (cb) { get('/api/stations', null, cb); },
        forecast:  function (stn, cb) { get('/api/forecast', stn ? { station: stn } : null, cb); },
        series:    function (stn, year, cb) { get('/api/series', { station: stn, year: year }, cb); }
    };
})(jQuery);
