import moment from 'moment-timezone';
import isArray from 'lodash/isArray';
import isObject from 'lodash/isObject'
import each from 'lodash/each';
import {some, findWhere} from "lodash";

import {REGEX, SUBSCRIPTION_TYPE} from 'utils/globals';
import {DATE_TIME_FORMATS, DISABLED_TXT, UNIX_SYMBOLIC_PERMISSION} from 'common-ui/utils/globals';
import f from 'common-ui/utils/f';
import UiState from 'common-ui/data/ui_state';

var Utils = {};

Utils.dateUtil = new function() {
    var that = this;

    this.getTimeZone = function(string, format) {
        return moment(string).format((format || DATE_TIME_FORMATS.DATEFORMAT));
    };
    this.getJSON = function(string) {
        return moment(string).toJSON();
    };
    this.getMomentUTC = function(string) {
        return moment.utc(string)
    };
    this.toJSON = function(format){
      if(format){
        return format.toJSON()
      }else{
        return undefined;
      }
    }
    this.getMomentObject = function(string) {
        if(string !== null){
          return moment(string)
        }else{
          return undefined;
        }
    }
    this.getValueOf = function(string) {
        if(string){
          return moment(string).valueOf();
        }else{
          return 0;
        }
    }
    this.momentInstance = function() {
        return moment;
    }
    this.getLocalTimeZoneDateObject = function(date, offset) {
        return new Date(date.setMinutes(-(date.getTimezoneOffset() + (offset))))
    }
    this.getTimeZoneDateObject = function(string) {
        return new Date(string)
    }
        /**
         * [getTimeZoneMomentDateObject it will return ]
         * @param  {[type]} option [require moment tz object]
         * @return {[type]}        [description]
         */
    this.getTimeZoneFromMomentObject = function(momentO) {
        if (momentO.isValid()) {
            var date = momentO.format('MM/DD/YYYY,HH:mm:ss.SSS').split(',');
            var dateObjectWithMilisecond = "";
            if (date[0] && date[1]) {
                var milliseconds = date[1].split('.');
                if (milliseconds[0] && milliseconds[1]) {
                    dateObjectWithMilisecond = new Date(date[0] + " " + milliseconds[0]);
                    dateObjectWithMilisecond.setMilliseconds(milliseconds[1]);
                } else {
                    dateObjectWithMilisecond = new Date(date[0]);
                }
                return dateObjectWithMilisecond;
            }
        } else {
            this.getLocalTimeZoneDateObject(((momentO.toDate()) ? (momentO.toDate()) : (new Date(momentO))));
        }
    }

    this.getMonthsList = () => {
        const months = Array.from({length: 12}, (e, i) => {
            return new Date(null, i + 1, null).toLocaleDateString("en", {month: "short"});
        })
        return months
    }

    this.getTimeDiff = function(option) {
        // If You have time more then 24 hours so moment returns 0 for HH:MM:SS so using this 3 line we get perfect time gap
        var self = this;
        var ms = moment(option[1], "DD/MM/YYYY HH:mm:ss").diff(moment(option[0], "DD/MM/YYYY HH:mm:ss"));
        var d = moment.duration(ms);
        var s = Math.floor(d.asHours()) + that.getMomentUTC(ms).format(":mm:ss");
        this.splitedValue = s.split(':');

        this.getHourDiff = function() {
            return parseInt(self.splitedValue[0]);
        };
        this.getMinuteDiff = function() {
            return parseInt(self.splitedValue[1]);
        };
        this.getSecondDiff = function() {
            return parseInt(self.splitedValue[2]);
        };
    }
    this.setTimeZone = function(zone) {
        moment.tz.setDefault(zone)
    }
    this.getRelativeDateString = function() {}

    this.getLast10Mins = function() {
        return [moment().minute(moment().minutes() - 10).seconds(moment().seconds() - 1), moment().minute(moment().minutes()).seconds(moment().seconds())];
    }
    this.getLast30Mins = function() {
        return [moment().minute(moment().minutes() - 30).seconds(moment().seconds() - 1), moment().minute(moment().minutes()).seconds(moment().seconds())];
    }
    this.getLast1HourRange = function() {
        return [moment().hour(moment().hours() - 1).minute(moment().minutes() - 1).seconds(moment().seconds() - 1), moment().hour(moment().hours()).minute(moment().minutes()).seconds(moment().seconds())];
    }
    this.getLast12HoursRange = function() {
        return [moment().hour(moment().hours() - 12).minute(moment().minutes() - 1).seconds(moment().seconds() - 1), moment().hour(moment().hours()).minute(moment().minutes()).seconds(moment().seconds())];
    }
    this.getLast24HoursRange = function() {
        return [moment().hour(moment().hours() - 24).minute(moment().minutes() - 1).seconds(moment().seconds() - 1), moment().hour(moment().hours()).minute(moment().minutes()).seconds(moment().seconds())];
    }
    this.getTodayRange = function() {
        return [moment().hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getYesterdayRange = function() {
        return [moment().subtract(1, 'days').hour('0').minute('0').seconds('01').milliseconds("000"), moment().subtract(1, 'days').hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLast5DaysRange = function() {
        return [moment().subtract(4, 'days').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLast7DaysRange = function() {
        return [moment().subtract(6, 'days').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLast15DaysRange = function() {
        return [moment().subtract(14, 'days').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLast30DaysRange = function() {
        return [moment().subtract(29, 'days').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getThisMonthRange = function() {
        return [moment().startOf('month').hour('0').minute('0').seconds('01').milliseconds("000"), moment().endOf('month').hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLastMonthRange = function() {
        return [moment().subtract(1, 'month').startOf('month').hour('0').minute('0').seconds('01').milliseconds("000"), moment().subtract(1, 'month').endOf('month').hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getLastThreeMonthRange = function() {
        return [moment().subtract('3', 'month').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")]
    }
    this.getLastSixMonthRange = function() {
        return [moment().subtract(6, 'month').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")]
    }
    this.getLastOneYearRange = function() {
        return [moment().subtract(1, 'year').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")]
    }
    this.getYearToDate = function() {
        return [moment().startOf('year').hour('0').minute('0').seconds('01').milliseconds("000"), moment().hour('23').minute('59').seconds('59').milliseconds("999")]
    }
    this.getThisMonthRangePreviousDate = function() {
        return [moment().startOf('month').hour('0').minute('0').seconds('01').milliseconds("000"), moment().subtract(1, 'days').hour('23').minute('59').seconds('59').milliseconds("999")];
    }
    this.getOneDayTimeDiff = function(checkTime, previousUnit) {
        var hourDiff = checkTime.getHourDiff();
        var seconDiff = checkTime.getSecondDiff();
        var minuteDiff = checkTime.getMinuteDiff();
        if (hourDiff <= 2) {

            if (hourDiff == 0) {
                if (minuteDiff == 0) {
                    var numString = parseInt(Utils.getNumString(previousUnit));
                    if (seconDiff == 0) {
                        if (numString && numString <= 100) {
                            return `+${Math.round(numString / 2)}MILLISECOND`;
                        }
                        return "+100MILLISECOND";
                    } else {
                        if (seconDiff > 30) {
                            return "+2SECOND";
                        } else if (seconDiff < 30 && seconDiff > 1) {
                            return "+500MILLISECOND";
                        } else {
                            if (numString && numString <= 100) {
                                return `+${Math.round(numString / 2)}MILLISECOND`;
                            }
                            return "+100MILLISECOND";
                        }
                    }

                } else {
                    if (minuteDiff > 30) {
                        return "+2MINUTE";
                    } else if (minuteDiff < 30 || minuteDiff > 1) {
                        return "+1MINUTE";
                    }
                }

            } else {
                if (hourDiff == 1) {
                    return "+2MINUTE";
                } else if (hourDiff == 2) {
                    return "+5MINUTE";
                }
            }
        } else if (hourDiff <= 6) {
            return "+5MINUTE";
        } else if (hourDiff <= 10) {
            return "+10MINUTE";
        } else {
            return "+1HOUR";
        }
    }
    this.getMonthDiff = function(startDate, endDate, dayGap, checkTime, previousUnit) {
        var dayDiff = (moment(endDate).diff(startDate, 'days'));
        if (dayDiff <= dayGap) {
            if (dayDiff == 0) {
                return this.getOneDayTimeDiff(checkTime, previousUnit)
            } else {
                return "+" + (moment(endDate).diff(startDate, 'days')) + "HOUR"
            }
        } else {
            return "+1DAY"
        }
    }
    this.calculateUnit = function(picker, previousUnit) {
      if(!picker.startDate || !picker.endDate){
        return undefined;
      }
        var dayGap = 10,
            startDate = new Date(picker.startDate.format('MM/DD/YYYY')),
            endDate = new Date(picker.endDate.format('MM/DD/YYYY')),
            now = new Date(moment().format('MM/DD/YYYY'));

        var checkTime = new that.getTimeDiff([picker.startDate.format('MM/DD/YYYY HH:mm:ss'), picker.endDate.format('MM/DD/YYYY HH:mm:ss')]);

        if ((moment(startDate).isSame(endDate)) && (moment(startDate).isSame(now))) {
            //console.log("today")
            return that.getOneDayTimeDiff(checkTime, previousUnit);
        } else if ((moment(startDate).isSame(endDate)) && (moment(startDate).isBefore(now))) {
            //console.log("yesterday")
            return that.getOneDayTimeDiff(checkTime, previousUnit);

        } else if ((moment(startDate).isBefore(now)) || (moment(now).diff(startDate, 'days'))) {
            if ((moment(now).diff(startDate, 'days')) === 6) {
                //console.log("last 7 days");
                return "+5HOUR";
            } else if ((moment(now).diff(startDate, 'days') === 29) || (moment(now).diff(startDate, 'days') === 28) || (moment(now).diff(startDate, 'days') === 30)) {
                //console.log("Last 30 days");
                return that.getMonthDiff(startDate, endDate, dayGap, checkTime, previousUnit);
            } else if ((moment(now).diff(startDate, 'month') === 1) && (moment(now).diff(startDate, 'days') > 30) && (moment(startDate).isSame(endDate, 'month'))) {
                //console.log("Last Month");
                return that.getMonthDiff(startDate, endDate, dayGap, checkTime, previousUnit);
            } else if ((moment(startDate).isSame(endDate, 'month')) && ((moment(now).diff(startDate, 'days') === 29) || (moment(now).diff(startDate, 'days') === 30) || (moment(now).diff(startDate, 'days') === 28))) {
                //console.log("this Month");
                return that.getMonthDiff(startDate, endDate, dayGap, checkTime, previousUnit);
            } else if ((moment(endDate).diff(startDate, 'days') >= 28) && (moment(endDate).diff(startDate, 'days') <= 30)) {
                //console.log("Last 30 days");
                return that.getMonthDiff(startDate, endDate, dayGap, checkTime, previousUnit);
            } else if ((moment(endDate).diff(startDate, 'month') > 3)) {
                return "+1MONTH";
            } else if ((moment(endDate).diff(startDate, 'month') < 3)) {
                if ((moment(endDate).diff(startDate, 'month')) === 0) {
                    return that.getMonthDiff(startDate, endDate, dayGap, checkTime, previousUnit);
                } else {
                    return "+1MONTH"
                }

            } else {
                return "+1MONTH";
            }
        } else {
            if ((moment(endDate).diff(startDate, 'days') < 10)) {
                return "+2HOUR";
            } else if ((moment(endDate).diff(startDate, 'days') > 15)) {
                return "+5HOUR";
            } else if ((moment(endDate).diff(startDate, 'days') <= 30)) {
                return "+1DAY";
            } else {
                return "+1MONTH";
            }
        }

    }
    this.calculateMaxDateUnit = function (picker, previousUnit) {
        if(!picker.startDate || !picker.endDate){
          return undefined;
        }
        const startDate = new Date(picker.startDate.format('MM/DD/YYYY')),
            endDate = new Date(picker.endDate.format('MM/DD/YYYY')),
            now = new Date(moment().format('MM/DD/YYYY'));

        if ((moment(startDate).isBefore(now)) && (moment(endDate).diff(startDate, 'month') > 3) && (moment(endDate).diff(startDate, 'month') <= 12)) {
            return "+1MONTH";
        } else if ((moment(startDate).isBefore(now)) &&(moment(endDate).diff(startDate, 'month') > 12) && (moment(endDate).diff(startDate, 'month') <= 24)) {
            return "+3MONTH";
        } else if ((moment(startDate).isBefore(now)) &&(moment(endDate).diff(startDate, 'month') > 24)) {
            return "+6MONTH";
        } else {
            return this.calculateUnit(picker, previousUnit);
        }
    }
    this.getRelativeDateFromString = function(string) {
        var obj = findWhere(Utils.relativeDates, {
            text: string
        })
        if (obj)
            return obj.fn && obj.fn();
    }
    this.timeDifference = function(startDate, endDate, format='HH:mm:ss') {
        return moment.utc(moment(endDate).diff(moment(startDate))).format(format);
    }
    this.timeDifference1 = function(startDate, endDate, format='HH:mm:ss') {
        return this.calculateDuration(moment(endDate).diff(moment(startDate)), format);
    }
    this.durationHumanize = (duration) => {
        if (duration == null) {
            return "";
        }
        duration = moment.duration(duration);
        let str = "";
        if(duration.days() > 1) str = str + Math.floor(duration.days()) + "d ";
        if(duration.hours() > 1) str = str + Math.floor(duration.hours()) + "h ";
        if(duration.minutes() > 1) str = str + Math.floor(duration.minutes()) + "m ";
        if(duration.seconds() > 1) str = str + Math.floor(duration.seconds()) + "s ";
        return str;
    }
    this.calculateDuration = function(duration, format='HH:mm:ss.SSS') {
        if (duration == null) {
            return ''
        }
        if (typeof duration == 'number') {
            duration = moment.duration(duration);
        }
        let time = moment.utc(duration.asMilliseconds()).format(format);
        let timediff = [];
        let years = duration.years();
        let months = duration.months();
        let days = duration.days();
        if (years) {
            timediff.push(`${years} year${years > 1 ? 's' : ''}`);
        }
        if (months) {
            timediff.push(`${months} month${months > 1 ? 's' : ''}`);
        }
        if (days) {
            timediff.push(`${days} day${days > 1 ? 's' : ''}`);
        }
        return `${timediff.join(' ')} ${time}`.trim();
    }
    this.daysDiff = function(startDate, endDate) {
        startDate = moment(startDate);
        endDate = moment(endDate);
        return startDate.diff(endDate, 'days');
    }
    this.getXAxisTickFormat = function(d, unit, d3) {
        let date = this.getTimeZoneFromMomentObject(this.getMomentObject(d));
        return d3.time.format(this.getFormatByUnit(unit))(date);
    }
    this.getFormatByUnit = function(unit='') {
        if ((unit.search('HOUR') + 1) || (unit.search('MINUTE') + 1)) {
            return '%H:%M - %m/%d/%y';
        }
        if (unit.search('MILLI') + 1) {
            return '%H:%M:%S.%L - %m/%d/%y';
        }
        if (unit.search('MONTH') + 1) {
            return '%b %d';
        }
        if (unit.search('SECOND') + 1) {
            return '%H:%M:%S - %m/%d/%y';
        }
        if (unit.search('7DAY') + 1) {
            return '%e. %b';
        }
        return '%m/%d/%y';
    }
    this.getMonthsBetweenDates = function(startDate, endDate) {
        var dateStart = moment(startDate);
        var dateEnd = moment(endDate);
        var timeValues = [];

        while (dateEnd > dateStart || dateStart.format('M') === dateEnd.format('M')) {
            timeValues.push(dateStart.format('MMM-YYYY'));
            dateStart.add(1, 'month');
        }
        return timeValues;
    }
    this.getDateRangesForMonth = function(startDate, endDate, monthBetweenDates) {
        let ranges = [];
        if (!monthBetweenDates) {
            monthBetweenDates = this.getMonthsBetweenDates(startDate, endDate);
            monthBetweenDates.splice(0, 1);
            monthBetweenDates.pop();
        }
        if (monthBetweenDates.length) {
            let lastDateOfStartDate = moment().year(startDate.year()).month(startDate.month()).endOf('month');
            let startRange = [startDate.toJSON(), lastDateOfStartDate.toJSON()];
            ranges.push(startRange);

            monthBetweenDates.forEach(monthYear => {
                let start = moment(`1-${monthYear}`, 'D-MMM-YYYY');
                let end = moment().year(start.year()).month(start.month()).date(start.daysInMonth()).hour('23').minute('59').seconds('59').milliseconds("999");
                ranges.push([start.toJSON(), end.toJSON()]);
            })
            let firstDateOfEndDate = moment().year(endDate.year()).month(endDate.month()).date('1').hour('0').minute('0').seconds('01').milliseconds("000");
            let endRange = [firstDateOfEndDate.toJSON(), endDate.toJSON()];
            ranges.push(endRange);
        } else {
            if (startDate.month() == endDate.month()) {
                ranges.push([startDate.toJSON(), endDate.toJSON()]);
            } else {
                let lastDateOfStartDate = moment().year(startDate.year()).month(startDate.month()).endOf('month').hour('23').minute('59').seconds('59').milliseconds("999");
                let startRange = [startDate.toJSON(), lastDateOfStartDate.toJSON()];
                ranges.push(startRange);
                let firstDateOfEndDate = moment().year(endDate.year()).month(endDate.month()).date('1').hour('0').minute('0').seconds('00').milliseconds("000");
                let endRange = [firstDateOfEndDate.toJSON(), endDate.toJSON()];
                ranges.push(endRange);
            }
        }

        return ranges;
    }

    this.getCalendar = function getCalendar(string, calendarConfig) {
        return moment(string).calendar(null, {
            lastDay : '[Yesterday at] LT',
            sameDay : '[Today at] LT',
            nextDay : '[Tomorrow at] LT',
            lastWeek : '[last] dddd [at] LT',
            nextWeek : 'dddd [at] LT',
            sameElse : 'DD/MM/YYYY h:mm:ss',
            ...calendarConfig
        });
    }
    this.getPreviousDatesFromGap = function (startDate, endDate) {
        const dayGap = this.daysDiff(endDate, startDate);
        const from = this.getMomentObject(startDate).subtract(dayGap + 1, 'days');
        const to = this.getMomentObject(startDate).subtract(1, 'days');
        return {
            from: from.toJSON(),
            to: to.toJSON()
        }
    }
    this.getPreviousDateRange = function (range) {
        const [from, to] = range;
        return [from.subtract(1, 'days'), to.subtract(1, 'days')];
    }
};

Utils.formatBytes = function(bytes,decimals) {
   if(bytes <= 0) return '0 Byte';
   if(!bytes) return '';
   var k = 1024; // or 1024 for binary
   var dm = decimals + 1 || 3;
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
   var i = Math.floor(Math.log(bytes) / Math.log(k));
   return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

Utils.graphUnitParse = function(unitVal){
    if(! unitVal){
        return "";
    }
    var numString = Utils.getNumString(unitVal);
    var str = unitVal.replace(/\d+/g, '').replace(/\+/g,'');
    return numString +" " + Utils.getCamelCase(str) + "(s) gap";
}

Utils.getNumString = function(unitVal) {
    if(! unitVal){
        return "";
    }
    var pattern = /(\d)\s+(?=\d)/g;
    var number = unitVal.match(/\d+/g).map(Number);
    return number.toString().replace(pattern , '$1');
}

Utils.getCamelCase = function(str){
    if(!str){
        return "";
    }
    var str = str.toLowerCase();
    return str.replace(/(?:^|\s)\w/g, function(match) {
        return match.toUpperCase()
    });
}

Utils.characterValidation = function(field, regEx, trimValue=true, errorMessage = ''){

    let re = regEx || /^[A-Za-z0-9-._\s]*$/;
    let isValid = false ;
    let value = trimValue ? (field.value || '').trim() : (field.value || '');

    if (value.length > 0) {
        if (re.test(value)) {
            isValid = true;
            field._originalErrorMessage = '';
        } else {
            field._originalErrorMessage = errorMessage || 'Special character [~!@#$%^&*(),|""] are not allowed.';
        } 
    } else {
        field._originalErrorMessage = 'Required!';
    }
    return isValid;
}

Utils.findMatchingElements = function(string, tagName) {
    let r = new RegExp(`<${tagName}>[\\s\\S]*?<\/${tagName}>`, 'gi');

    return string.match(r) || [];
}

Utils.stringShorten = function(str, length=20) {
    if (str.length <= length) {
        return str;
    }

    let startRegExp = new RegExp('^(\/?[a-z._\/0-9]{8})', 'gi');
    let endRegExp = new RegExp('([a-z._\/0-9]{8})$', 'gi');

    let startRegList = str.match(startRegExp);
    let endRegList = str.match(endRegExp);

    return [...startRegList, ...endRegList].join('....');
}

Utils.toFixed = function(value, toFixed=2) {
    if (value == null) {
        return '';
    }
    return parseFloat(value).toFixed(toFixed)
}

Utils.dateRangePickerRange = function() {
    let ranges = {
        'Today': Utils.dateUtil.getTodayRange(),
        'Yesterday': Utils.dateUtil.getYesterdayRange(),
        'Last 7 Days': Utils.dateUtil.getLast7DaysRange(),
        'Last 30 Days': Utils.dateUtil.getLast30DaysRange(),
        'This Month': Utils.dateUtil.getThisMonthRange(),
        'Last Month': Utils.dateUtil.getLastMonthRange()
    }
    Object.defineProperty(ranges, 'Today', {get: function() { return Utils.dateUtil.getTodayRange();}});
    Object.defineProperty(ranges, 'Yesterday', {get: function() { return Utils.dateUtil.getYesterdayRange();}});
    Object.defineProperty(ranges, 'Last 7 Days', {get: function() { return Utils.dateUtil.getLast7DaysRange();}});
    Object.defineProperty(ranges, 'Last 30 Days', {get: function() { return Utils.dateUtil.getLast30DaysRange();}});
    Object.defineProperty(ranges, 'This Month', {get: function() { return Utils.dateUtil.getThisMonthRange();}});
    Object.defineProperty(ranges, 'Last Month', {get: function() { return Utils.dateUtil.getLastMonthRange();}});
    return ranges;
}
Utils.billingDateRangePickerRange = function() {
    let ranges = {
        'This Month': Utils.dateUtil.getThisMonthRange(),
        'Last Month': Utils.dateUtil.getLastMonthRange()
    }
    Object.defineProperty(ranges, 'This Month', {get: function() { return Utils.dateUtil.getThisMonthRange();}});
    Object.defineProperty(ranges, 'Last Month', {get: function() { return Utils.dateUtil.getLastMonthRange();}});
    return ranges;
}

Utils.telemetryDateRangePickerRange = function() {  
    let ranges = {
        'Yesterday': Utils.dateUtil.getYesterdayRange(),
        'Last 7 Days': Utils.dateUtil.getLast7DaysRange(),
        'Last 30 Days': Utils.dateUtil.getLast30DaysRange(),
        'This Month': Utils.dateUtil.getThisMonthRangePreviousDate(),
        'Last Month': Utils.dateUtil.getLastMonthRange(),
        'Last 3 Months': Utils.dateUtil.getLastThreeMonthRange(),
        'Last 6 Months': Utils.dateUtil.getLastSixMonthRange(),
        'Last 1 Year': Utils.dateUtil.getLastOneYearRange()
    }
    Object.defineProperty(ranges, 'Yesterday', {get: function() { return Utils.dateUtil.getYesterdayRange();}});
    Object.defineProperty(ranges, 'Last 7 Days', {get: function() { return Utils.dateUtil.getLast7DaysRange();}});
    Object.defineProperty(ranges, 'Last 30 Days', {get: function() { return Utils.dateUtil.getLast30DaysRange();}});
    Object.defineProperty(ranges, 'This Month', {get: function() { return Utils.dateUtil.getThisMonthRangePreviousDate();}});
    Object.defineProperty(ranges, 'Last Month', {get: function() { return Utils.dateUtil.getLastMonthRange();}});
    Object.defineProperty(ranges, 'Last 3 Months', {get: function() { return Utils.dateUtil.getLastThreeMonthRange()}});
    Object.defineProperty(ranges, 'Last 6 Months', {get: function() { return Utils.dateUtil.getLastSixMonthRange()}});
    Object.defineProperty(ranges, 'Last 1 Year', {get: function() { return Utils.dateUtil.getLastOneYearRange()}});
    return ranges;
}
Utils.solrDateRangePickerRangeProps = function() {
    let ranges = {
        'Today': Utils.dateUtil.getTodayRange(),
        'Yesterday': Utils.dateUtil.getYesterdayRange(),
        'Last 5 Days': Utils.dateUtil.getLast5DaysRange(),
        'Last 15 Days': Utils.dateUtil.getLast15DaysRange(),
        'Last 30 Days': Utils.dateUtil.getLast30DaysRange(),
    }
    Object.defineProperty(ranges, 'Today', {get: function() { return Utils.dateUtil.getTodayRange();}});
    Object.defineProperty(ranges, 'Yesterday', {get: function() { return Utils.dateUtil.getYesterdayRange();}});
    Object.defineProperty(ranges, 'Last 5 Days', {get: function() { return Utils.dateUtil.getLast5DaysRange();}});
    Object.defineProperty(ranges, 'Last 15 Days', {get: function() { return Utils.dateUtil.getLast15DaysRange();}});
    Object.defineProperty(ranges, 'Last 30 Days', {get: function() { return Utils.dateUtil.getLast30DaysRange();}});
    return {
        ranges : ranges,
        dateRangePickerAttr: {
            minDate: Utils.dateUtil.momentInstance()().subtract(29, "days")
        }
    }
}

Utils.stringToArray = function(string, splitBy=',') {
    if (!string) return [];
    if (!string.slice) {
        return [];
    }
    return Array.isArray(string.slice()) ? string : string.split(splitBy);
}

Utils.parseJSON = function(json = "", defaultValue={}) {
    let parseJson;
    try {
        parseJson = JSON.parse(json);
    } catch (e) {
        parseJson = defaultValue;
    }
    return parseJson;
}

Utils.getUnixSymbolicPermission = function(permission) {
    return UNIX_SYMBOLIC_PERMISSION[permission] || '';
}

Utils.localStorage = {
    checkLocalStorage: function(key, value) {
        if (typeof(Storage) !== "undefined") {
            return this.getLocalStorage(key, value);
        } else {
            console.log('Sorry! No Web Storage support');
            Utils.cookie.checkCookie(key, value);
        }
    },
    setLocalStorage: function(key, value) {
        localStorage.setItem(key, value);
        return {
            found: false,
            'value': value
        };
    },
    getLocalStorage: function(key, value) {
        var keyValue = localStorage.getItem(key)
        if (!keyValue || keyValue == "undefined") {
            return this.setLocalStorage(key, value);
        } else {
            return {
                found: true,
                'value': keyValue
            };
        }
    }

}
Utils.cookie = {
    setCookie: function(cname, cvalue) {
        document.cookie = cname + "=" + cvalue + "; "
        return {
            found: false,
            'value': cvalue
        };
    },
    getCookie: function(findString) {
        var search = findString + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1);
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    },
    checkCookie: function(key, value) {
        var findString = getCookie(key);
        if (findString != "" || keyValue != "undefined") {
            return {
                found: true,
                'value': ((findString == "undefined") ? (undefined) : (findString))
            };
        } else {
            return setCookie(key, value);
        }
    }
}

Utils.getMaxOfArray = function(numArray) {
  return Math.max.apply(null, numArray);
}

Utils.isValidRegex = function(expression) {
    try {
        RegExp(expression);
    } catch (e) {
        return false;
    }
    return true;
}

Utils.smartTrim = function(string, maxLength) {
    if (!string) {return string;}
    if (maxLength < 1) {return string;}
    if (string.length <= maxLength) {return string;}
    if (maxLength == 1) {return string.substring(0, 1) + '...';}
    //if (string.length <= maxLength + 3) {maxLength = maxLength - 3}

    var midpoint = Math.ceil(string.length / 2);
    var toremove = string.length - maxLength;
    var lstrip = Math.ceil(toremove / 2);
    var rstrip = toremove - lstrip;
    return string.substring(0, midpoint - lstrip) + '...' + string.substring(midpoint + rstrip);
}

Utils.resourceTrim = function(string, splitBy="/") {
    if (!string) {return string;}
    if (typeof string != "string") {return string;}
    let arrOfString = string.split(splitBy);
    if (arrOfString.length <= 3) {return string;}
    if (arrOfString[0] == "") {return `${splitBy}${arrOfString[1]}${splitBy}...${splitBy}${arrOfString[arrOfString.length - 1]}`}
    return `${arrOfString[0]}${splitBy}...${splitBy}${arrOfString[arrOfString.length - 1]}`;
}

Utils.clearTimeout = function(timer) {
    window.clearTimeout(timer);
}

Utils.getLines = function(text="", noOfLines=5, splitBy="\n") {
    text = text && text.split(splitBy);
    let lines = {
        text: text && text.splice(0, noOfLines).join(splitBy),
        length: text && text.length || 0
    }
    return lines;
}

Utils.dataURIToBlob = function(dataURI) {
    dataURI = dataURI.replace(/^data:/, '');

    const type = dataURI.match(/application\/[^;]+/);
    const base64 = dataURI.replace(/^[^,]+,/, '');

    var binary_string = atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++)        {
        bytes[i] = binary_string.charCodeAt(i);
    }
    bytes.buffer;

    return new Blob([bytes.buffer], {type});
}

Utils.toQueryParams = function(params={}) {
    return Object.keys(params).filter(k => params[k] != null).map(key => key + '=' + params[key]).join('&');
}

Utils.wildcardMatch = function(find='', source) {
    find = find.replace(/[\-\[\]\/\{\}\(\)\+\.\\\^\$\|]/g, "\\$&")
        .replace(/\*/g, ".*")
        .replace(/\?/g, ".");
    var regEx = new RegExp('^'+find, "i");
    return regEx.test(source);
}

Utils.cloneDeep = data => {
    return JSON.parse(JSON.stringify(data));
}

Utils.getOptions = ({ resp, searchString, labelKey = 'label', valueKey = 'value', pageSize }) => {
    const options = resp.models.slice();
    const totalCount = resp.raw.rawResponse.data.totalElements;
    if (totalCount > pageSize) {
        const labelValue = `+ ${totalCount - pageSize}`;
        options.push({
            [labelKey]: labelValue,
            valueKey: searchString,
            disabled: true
        });
    }
    return options;
}

Utils.emptyOptions = ({ labelKey = 'label', valueKey = 'value' }) => {
    return [{
        [labelKey]: 'Type to search',
        [valueKey]: '',
        disabled: true
    }]
}

Utils.copyToClipboard = function(containerid) {
    if (!containerid) {
        return;
    }
    var selector = document.getElementById(containerid) || document.createElement('div');
    var range = document.createRange();
    range.selectNodeContents(selector);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);

    try{
        document.execCommand('copy')
    }catch(e) {
        console.log(e)
    }
    selection.removeAllRanges();
}
Utils.copyToClipboardV2 = function(containerid, dataAttributeName='data-clipboard-text', textToCopy='') {
    var selector = document.getElementById(containerid) || document.createElement('div');

    var clone = document.createElement('div');
    clone.style.position = 'absolute';
    clone.style.left = '-9999px';

    document.body.appendChild(clone);
    clone.innerText = selector.getAttribute(dataAttributeName) || textToCopy;
    var range = document.createRange();
    range.selectNodeContents(clone);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);

    try{
        document.execCommand('copy')
    }catch(e) {
        console.log(e)
    }
    selection.removeAllRanges();
    document.body.removeChild(clone);
}

Utils.isSafari = function isSafari(){
    return /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));
}

Utils.downloadFile = function(response, defaultFileName='file') {
    //get the file
    var octetStreamMime = 'application/octet-stream';

    //get the headers' content disposition
    var cd = response.headers["content-disposition"];

    //get the file name with regex
    var regex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    var match = regex.exec(cd);

    //is there a fiel name?
    var fileName = match[1] || defaultFileName;

    //replace leading and trailing slashes that C# added to your file name
    fileName = fileName.replace(/\"/g, "");

    //determine the content type from the header or default to octect stream
    var contentType = response.headers["content-type"] || octetStreamMime;

    //finally, download it
    try {
        var blob = new Blob([response.data], {type: contentType});

        //downloading the file depends on the browser
        //IE handles it differently than chrome/webkit
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveOrOpenBlob(blob, fileName);
        } else {
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.style = "display: none";
            a.href = url;
            a.download = fileName;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    } catch (exc) {
        console.log("Save Blob method failed with the following exception.");
        console.log(exc);
    }
}

Utils.encodeURI = function(val='') {
    if (typeof val != 'string') {
        val = JSON.stringify(val);
    }
    return encodeURI(val);
}

Utils.decodeURI = function(val) {
    if (val) {
        return decodeURI(val)
    }
    return val;
}

Utils.encodeURIComponent = (val='') => {
    if (typeof val != 'string') {
        val = JSON.stringify(val);
    }
    return encodeURIComponent(val);
}

Utils.decodeURIComponent = str => {
    if (str) {
        return decodeURIComponent(str)
    }
    return str;
}

Utils.geo = function() {
    var self = this;
    var tolerance = 1e-10;

    function eq(a, b) {
        return (Math.abs(a - b) < tolerance);
    }

    function gt(a, b) {
        return (a - b > -tolerance);
    }

    function lt(a, b) {
        return gt(b, a);
    }

    this.eq = eq;
    this.gt = gt;
    this.lt = lt;

    this.LineSegment = function(x1, y1, x2, y2) {
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;

        // Ax + By = C
        this.a = y2 - y1;
        this.b = x1 - x2;
        this.c = x1 * this.a + y1 * this.b;

        if (eq(this.a, 0) && eq(this.b, 0)) {
            throw new Error(
                'Cannot construct a LineSegment with two equal endpoints.');
        }
    };

    this.LineSegment.prototype.intersect = function(that) {
        var d = (this.x1 - this.x2) * (that.y1 - that.y2) -
            (this.y1 - this.y2) * (that.x1 - that.x2);

        if (eq(d, 0)) {
            // The two lines are parallel or very close.
            return {
                x: NaN,
                y: NaN
            };
        }

        var t1 = this.x1 * this.y2 - this.y1 * this.x2,
            t2 = that.x1 * that.y2 - that.y1 * that.x2,
            x = (t1 * (that.x1 - that.x2) - t2 * (this.x1 - this.x2)) / d,
            y = (t1 * (that.y1 - that.y2) - t2 * (this.y1 - this.y2)) / d,
            in1 = (gt(x, Math.min(this.x1, this.x2)) && lt(x, Math.max(this.x1, this.x2)) &&
                gt(y, Math.min(this.y1, this.y2)) && lt(y, Math.max(this.y1, this.y2))),
            in2 = (gt(x, Math.min(that.x1, that.x2)) && lt(x, Math.max(that.x1, that.x2)) &&
                gt(y, Math.min(that.y1, that.y2)) && lt(y, Math.max(that.y1, that.y2)));

        return {
            x: x,
            y: y,
            in1: in1,
            in2: in2
        };
    };

    this.LineSegment.prototype.x = function(y) {
        // x = (C - By) / a;
        if (this.a) {
            return (this.c - this.b * y) / this.a;
        } else {
            // a == 0 -> horizontal line
            return NaN;
        }
    };

    this.LineSegment.prototype.y = function(x) {
        // y = (C - Ax) / b;
        if (this.b) {
            return (this.c - this.a * x) / this.b;
        } else {
            // b == 0 -> vertical line
            return NaN;
        }
    };

    this.LineSegment.prototype.length = function() {
        return Math.sqrt(
            (this.y2 - this.y1) * (this.y2 - this.y1) +
            (this.x2 - this.x1) * (this.x2 - this.x1));
    };

    this.LineSegment.prototype.offset = function(x, y) {
        return new self.LineSegment(
            this.x1 + x, this.y1 + y,
            this.x2 + x, this.y2 + y);
    };
    return this;
}

Utils.filterByName = function(entities, filterValue, field) {
    if (REGEX.ESCAPE_SPECIAL_CHAR.test(filterValue)) {
        filterValue = filterValue.replace(REGEX.ESCAPE_SPECIAL_CHAR, '');
    }
    let matchFilter = new RegExp(filterValue, 'i');
    return entities.filter(filteredList => !filterValue || searchFields(filteredList, matchFilter, field));
}

const  searchFields = (filteredList, matchFilter, field) => {
    if (typeof field === "string") {
        return matchFilter.test(filteredList[field]);
    } else if (isArray(field)) {
        return field.some(f => {
            let list = filteredList[f];
            if (list && list.slice) {
                list = list.slice();
            }
            if (isArray(list)) {
                return list.some(_f => {
                    const _o = isObject(_f) ? _f.label : _f;
                    return matchFilter.test(_o);
                })
            } else {
                return matchFilter.test(filteredList[f]);
            }
        })
    } else if (typeof filteredList === "string") {
        return matchFilter.test(filteredList);
    } else {
        return filteredList;
    }
}

const _pipe = (a, b) => (arg) => b(a(arg));
Utils.pipe = (...ops) => ops.reduce(_pipe);

Utils.ReadJSONFile = file => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsText(file);
        reader.onload = function(e) {
            try {
                const json = JSON.parse(e.target.result);
                resolve(json);
            } catch (err) {
                reject(err.message);
            }
        };
        reader.onerror = function() {
            reject(reader.error);
        };
    });
}

Utils.replaceSlashToEncodedChar = string => {
    if (!string) {
        return;
    }
    return string.replace(/\//g, "%2F");
}

Utils.GAevent = (ReactGA, method, ctg, ...otherArgs) => {
    if(!method || method.toLowerCase() == 'get') return;
    let category = ctg && ctg.replace(/\//g, "_").replace('api_'," ").replace(/(\d+)/,"").toUpperCase();
    let action = '';
    let label = `${category}_SECTION`;
    switch(method.toLowerCase()){
        case 'post':
            action = `Created new ${category}`;
            break;
        case 'put':
            action = `Updated ${category} data`;
            break;
        case 'delete':
            action = `Deleted ${category}`;
            break;
        default:
            action = `User perfomed action on ${category}`;
    }
    ReactGA?.event({
        category: category || '',
        action: action || '',
        label: label || ''
    });
};

/**
 * @param { Promise } promise
 * @param { Object } extendErrMsg - If you need to enhance the error.
 * @return { Promise }
 */
Utils.handlePromise = (promise, extendErrMsg) => {
    return promise
      .then(data => [null, data])
      .catch(err => {
        if (extendErrMsg) {
          Object.assign(err, extendErrMsg);
        }
        return [err]; // which is same as [err, undefined];
      });
}

/**
 * @param { coll } coll - promise collection
 * @param { err } extendErrMsg - If you need to enhance the error.
 * @param { data } data - response api data
 * @param { callback } callback
 */
Utils.handlePromiseError = ( coll, err, data, cb ) => {
    if (err) {
        f.resetCollection(coll, []);
        f.handleError(null)(err);   
        return err;
    } else {
        cb && cb(null,data);
        return data;
    }
}

/**
 * @param { Promise } promise
 * @param { Object } extendErrMsg - If you need to enhance the error.
 * @return { Promise }
 */
Utils.handlePromise = (promise, extendErrMsg) => {
    return promise
      .then(data => [null, data])
      .catch(err => {
        if (extendErrMsg) {
          Object.assign(err, extendErrMsg);
        }
        return [err]; // which is same as [err, undefined];
      });
}

/**
 * @param { coll } coll - promise collection
 * @param { err } extendErrMsg - If you need to enhance the error.
 * @param { data } data - response api data
 * @param { callback } callback
 */
Utils.handlePromiseError = ( coll, err, data, cb ) => {
    if (err) {
        f.resetCollection(coll, []);
        f.handleError(null)(err);   
        return err;
    } else {
        cb && cb(null,data);
        return data;
    }
}


Utils.getDynamicFieldWidth = (attr, collection, context) => {
    let width = 200;
    if (!context.wrapText) {
        for (let i = 0; collection.length > i ; i++) {
            const str = (collection[i][attr] || '').replace(/['"]+/g, '');
            let num = str.toString().length;
            const pNode = document.querySelector(`[data-field='${str}']`);
            if (pNode && pNode.style.display === "none") {
                continue ;
            }
            num = (+num * 7.5);
            if (width < num) {
                width = num;
            }
        }
    }
    return width;
}

//format big number with k and m    
Utils.formatDigits = (longNumber) => {  
    let final_d = '';   
    if(Math.abs(longNumber) >= 1000000) { // m  
        final_d = Math.sign(longNumber)*((Math.abs(longNumber)/1000000).toFixed(1)) + ' m'; 
    } else if (Math.abs(longNumber) > 9999){ // k   
        final_d = Math.sign(longNumber)*((Math.abs(longNumber)/1000).toFixed(1)) + ' k';    
    } else {    
        final_d = Math.sign(longNumber)*Math.abs(longNumber);   
    }   
    return final_d; 
}

Utils.handleDeprecatedProps = props => {
    const obj = Object.assign({
        variant: props.bsStyle || props.variant || undefined,
        bsPrefix: props.bsClass || props.bsPrefix || undefined,
        as: props.componentClass  || props.as || undefined,
        size: props.bsSize || props.bssize || props.size || undefined
    }, props);
    delete  obj.bsStyle;
    delete  obj.bsClass;
    delete  obj.bsSize;
    delete  obj.componentClass
    if (!obj.variant) delete obj.variant;
    if (!obj.bsPrefix) delete obj.bsPrefix;
    if (!obj.as) delete obj.as;
    if (!obj.size) delete obj.size;

    return obj;
}

Utils.excludeProps = (props, excludeList) => {
    excludeList.forEach(el => {
        if (props.hasOwnProperty(el)) {
            delete props[el]
        }
    });
    return props;
}

Utils.deepClone = data => {
    return JSON.parse(JSON.stringify(data));
}

Utils.toTitleCase = (str) => {
    if (str) {
        return str.replace(/\w\S*/g,
            (txt) => {
              return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }
        );
    }
    return '';
}

Utils.validateKeyValueProperty = (attributes) => {
    let msg = '';
    let isValid = true;
    let list = new Set();
    isValid = !some(attributes, (prop) => {
        if(list.has(prop.name)){
            msg = 'Attributes : Duplicate key name is not allowed!'
            return true;
        } else if(!! (!(prop.name && prop.value) && (prop.name || prop.value))){
            msg = 'Attributes : Please enter key/value!';
            return true;
        }
        list.add(prop.name);
    } );
    return { isValid, msg };
}

Utils.getUniquePath = (path = "", params = {}) => {
    return path + JSON.stringify(params);
};

Utils.getDiffFromCurDateInDaysAndHours = (dateParam) => {
    let date = moment(dateParam);

    let duration = moment.duration(date.diff(moment()));
    let days = date.diff(moment(), 'days');
    let hours = duration.hours();
    let minutes = duration.minutes();
    let seconds = duration.seconds();

    /*

    let minutes = date.diff(moment(), 'minutes');
    let seconds = date.diff(moment(), 'seconds');*/
    let dateToDaysAndHours = [];
    if (days > 0) {
        dateToDaysAndHours.push(`${days} day${days > 1 ? 's' : ''}`);
    }
    if (hours > 0) {
        dateToDaysAndHours.push(`${hours} hr${hours > 1 ? 's' : ''}`);
    } else if (minutes > 0) {
        dateToDaysAndHours.push(`${minutes} min${minutes > 1 ? 's' : ''}`);
    } else if (seconds > 0) {
        dateToDaysAndHours.push(`${seconds} sec${seconds > 1 ? 's' : ''}`);
    }
    if (dateToDaysAndHours.length) {
        dateToDaysAndHours = dateToDaysAndHours.join(' ');
    } else {
        dateToDaysAndHours = null;
    }
    return dateToDaysAndHours;
}

Utils.checkIfPermanentAccount = (subscriptionType = "") => {
    return (subscriptionType || "").toLowerCase() === SUBSCRIPTION_TYPE.PERMANENT.value.toLowerCase()
}

Utils.checkIfTrialExtendedAccount = (subscriptionType = "") => {
    return (subscriptionType || "").toLowerCase() === SUBSCRIPTION_TYPE.TRIAL_EXTENDED.value.toLowerCase()
}

Utils.getCommonSliderFilterCount = (filters) => {
    let count = 0;
    each(filters, (filter) => {
        if(filter.value){
            count += filter.value.length;
        }
    });
    return count;
}

Utils.convertPrivateKeyToString = (str = '') => {
    let key = 'KEY-----';

    //index to get start string
    let index = str.indexOf(key);
    let startString = str.substring(0, [index + key.length]);

    //index to get end string
    index = str.indexOf('-----END');
    let endString = str.substring(index, str.length);

    //replace start and end string to get private key
    str = str.replace(startString, '');
    str = str.replace(endString, '');

    //remove all space
    let privateKey = str.replace(/\s+/g, '');

    //recreate private key
    privateKey = startString + '\n' + privateKey + '\n' + endString;

    return privateKey;
}

Utils.scrollElementIntoView = (elementId) => {
    const element = document.getElementById(elementId)
    if (element) {
        element.scrollIntoView({behavior: "smooth"})
    }
}

Utils.commaStringValuesToArray = (json={}) => {
    Object.keys(json).forEach(key => {
        let value = json[key];
        if (typeof value == 'string') {
            json[key] = value.split(',').map(prop => prop.trim());
        } else if (typeof value == 'object') {
            json[key] = Utils.commaStringValuesToArray(value);
        }
    });
    return json;
}

Utils.replaceNumberWithString = (text='', replaceWith='.<index>.', regex=REGEX.DOT_INDEX_DOT) => {
    if (typeof text != 'string') {
        return text;
    }
    return text.replace(regex, replaceWith);
}

Utils.getNumberFromString = (actualString = '', templateString) => {
    let before = templateString.substring(0, templateString.indexOf('<'));
    let after = templateString.substring(templateString.indexOf('>') + 1);

    let number = actualString.replace(before, '');
    number = number.replace(after, '');

    return number;
}

Utils.getFirstIndex = (actualString = '', templateString = '') => {
    let before = templateString.substring(0, templateString.indexOf('<'));

    let number = actualString.replace(before, '');
    number = number.substring(0, number.indexOf('.'));
    return number;
}

Utils.getLastIndex = (actualString = '', templateString = '') => {
    let after = templateString.substring(templateString.lastIndexOf('>') + 1);

    let number = actualString.replace(after, '');
    number = number.substring(number.lastIndexOf('.') + 1);
    return number;
}

Utils.hasMultipleIndex = (actualString = '', templateString = '<index>') => {
    let firstIndex = actualString.indexOf(templateString);
    let lastIndex = actualString.lastIndexOf(templateString);

    return firstIndex != lastIndex;
}

Utils.booleanStringConversion = str => {
    return new RegExp("true").test(str);
}

Utils.setApplicationNamesInModels = (models=[], showDisabledStatus=true) => {
    let apps = [];
    const disabledStatusTxt = showDisabledStatus ? DISABLED_TXT : '';
    models.forEach((app) => {
        if (UiState.isCloudEnv()) {
            const name = `${app.name}${app.enableDiscovery ? '' : disabledStatusTxt}`;
            apps.push({...app,
                name,
                appName: name,
                value: app.uniqueCode,
                applicationFullName: name
            });
        } else {
            let obj = {};
            // app.application is there only when we are fetching system application for Platform
            if (app.hasOwnProperty('applications')) {
                const applications = app.applications || [];
                applications.forEach((application) => {
                    const name = `${app.name}-${application.name}${application.enableDiscovery ? '' : disabledStatusTxt}`;
                    apps.push({ ...application, systemName: app.name, appName: application.name, name: name, applicationFullName: name, value: application.uniqueCode });
                })
            } else {
                // when we are fetching dictionary application for Platform
                const name = `${app.name}-${app.enableDiscovery ? '' : disabledStatusTxt}`;
                apps.push({ ...app, appName: app.name, name: name, applicationFullName: name, value: app.uniqueCode });
            }
        }
    })
    return apps;
}

Utils.decodeBase64 = (base64String='') => {
    const binaryString = atob(base64String);
    return new TextDecoder('utf-8').decode(
        new Uint8Array([...binaryString].map(char => char.charCodeAt(0)))
    );
}

export {
    Utils
}