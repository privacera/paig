/* library imports */
import React, {Component} from 'react';
import { each } from 'lodash';
import jstz from 'jstimezonedetect';
import moment from 'moment-timezone';

// Material Imports
import NativeSelect from '@material-ui/core/NativeSelect';
import Chip from '@material-ui/core/Chip';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';

// Other imports
import {timezone} from './timezone';
import {Utils} from 'common-ui/utils/utils';

const TZ = {
    currentTimezone: '',
    timeZone: '',
    zoneName: '',
    selectedTimeZoneString: '',
    getMomentObject: function() {
       return moment; 
    },
    setTimeZone: function() {
        let storeTimezone = Utils.localStorage.checkLocalStorage('timezone');
        let systemZone = jstz.determine().name();
        let timezone;

        if (!storeTimezone.value || storeTimezone.value == "undefined") {
            Utils.localStorage.setLocalStorage('timezone', systemZone);
            storeTimezone.value = systemZone;
        }

        if (storeTimezone.value.split(',').length > 1) {
            timezone = storeTimezone.value.split(',')[0];
        } else {
            timezone = systemZone;
        }

        this.currentTimezone = storeTimezone;
        this.timeZone = timezone;
        this.zoneName = moment.tz(timezone).zoneName();
        moment.tz.setDefault(timezone);
    },

    getCurrentTimeZone: function() {
        let storeTimezone = Utils.localStorage.checkLocalStorage('timezone');
        let zoneName = this.zoneName = moment.tz(storeTimezone.value.split(',')[0]).zoneName();
        let splitStoreTimeZone = storeTimezone.value.split(',');

        if (splitStoreTimeZone.length) {
            if (splitStoreTimeZone[1] && splitStoreTimeZone[1] != zoneName) {
                Utils.localStorage.setLocalStorage('timezone', splitStoreTimeZone[0] + "," + zoneName);
            }
            this.timeZone = storeTimezone.value.split(',')[0];
        }

        return this.currentTimezone = storeTimezone;
    },

    reloadTimeZone: function() {
        Utils.localStorage.setLocalStorage('timezone', TZ.selectedTimeZoneString);
        window.location.reload();
    }
}

TZ.setTimeZone();

const getTimeZoneObj = () => {
    let storeTimezone = TZ.getCurrentTimeZone();
    let selectedtimeZone = '';
    if (!storeTimezone) {
        return;
    }
    if (storeTimezone != "undefined") {
        selectedtimeZone = storeTimezone.value;
    }

    selectedtimeZone = selectedtimeZone.split(',');
    let selectedTimeZone = '';
    let selectedZoneName = '';
    if (selectedtimeZone.length <= 1) {
        selectedTimeZone = TZ.timeZone;
        selectedZoneName = TZ.zoneName;
    } else {
        if (selectedtimeZone[2] && parseInt(selectedtimeZone[2]) <= 1) {
            selectedTimeZone = TZ.timeZone;
            selectedZoneName = TZ.zoneName;
        } else {
            selectedTimeZone = '';
            selectedZoneName = TZ.zoneName;
        }
    }
    return {
        selectedTimeZone,
        selectedZoneName
    }
}
class TimeZoneWorldMap extends Component {

    state = {
        quickLinks: this.getQuickLinksList(),
        hoverText: '',
        hoverZoneName: '',
        /*selectedTimeZone: '',
        selectedZoneName: ''*/
        ...getTimeZoneObj()
    }

    constructor(props) {
        super(props);
    }

    getDataAttributes = (attributes) => {
        const d = {};
        let re_dataAttr = /^data\-(.+)$/;

        each(attributes, (attr) => {
            if (re_dataAttr.test(attr.nodeName)) {
                const key = attr.nodeName.match(re_dataAttr)[1];
                d[key] = attr.nodeValue;
            }
        })

        return d;
    }

    getValue() {
        let values = [];
        [...document.querySelectorAll('polygon[data-selected="true"]')].forEach(p => {
            values.push(p.dataset || this.getDataAttributes(p.attributes));
        })
        return values;
    }

    getSelectedString() {
        setTimeout(() => {
            var valueArray = this.getValue();
            if (valueArray.length) {
                if (TZ.selectedTimeZoneString != valueArray[0].zonename) {
                    TZ.selectedTimeZoneString = valueArray[0].timezone + "," + valueArray[0].zonename + "," + valueArray.length
                    //TZ.changedTimeZone = true;
                }
            }
        }, 0);
    }

    getQuickLinksList() {
        const {timezoneList, quickLinks} = this.props;
        let list = [];
        Object.entries(quickLinks[0]).forEach(([label, value]) => {
            let tz = timezoneList.find(tz => {
                return tz.timezone == value || tz.zoneName == value;
            })
            if (tz) {
                list.push({label: label, value: value, timezone: tz.timezone, zoneName: tz.zoneName})
            }
        })
        return list;
    }
    timeZoneList = () => {
        const { timezoneList } = this.props;

        return (
            <NativeSelect fullWidth value={this.state.selectedTimeZone} variant="standard"
            onChange={(e) => {
                this.setState({
                    selectedTimeZone: e.target.value,
                    selectedZoneName: e.target.options[e.target.selectedIndex].dataset.zonename
                })
                this.getSelectedString();
            }} >
                {timezoneList.map( (tz,i) => {
                    return (
                        <option key={i} value={tz.timezone} data-zonename={tz.zoneName} >
                            {tz.timezone} ({tz.zoneName})
                        </option>
                    )
                })}
            </NativeSelect>
        )
    }
    generateWorldMap = () => {
        const {timezoneList, dayLightSaving, width, height} = this.props;
        const {hoverZoneName, selectedTimeZone, selectedZoneName} = this.state;
        let viewBox = `0 0 ${width} ${height}`;
        let m = moment;
        return (
            <svg className="timezone-map" viewBox={viewBox}>
                {timezoneList.map((tz, i) => {
                        return (
                            <polygon
                                key={i}
                                className={hoverZoneName == tz.zoneName ? 'active' : '' }
                                data-timezone={tz.timezone}
                                data-country={tz.country}
                                data-pin={tz.pin}
                                data-offset={tz.offset}
                                points={tz.points}
                                data-zonename={dayLightSaving ? (moment().tz(tz.timezone).zoneName()) : tz.zoneName}
                                data-selected={ (selectedTimeZone == tz.timezone || (!selectedTimeZone && selectedZoneName == tz.zoneName) ) }
                                onMouseEnter={(e) => {

                                    this.setState({
                                        hoverText: `${e.target.getAttribute('data-timezone')} (${e.target.getAttribute('data-zonename')})`,
                                        hoverZoneName: e.target.getAttribute('data-zonename')
                                    });
                                }}
                                onMouseLeave={e => {
                                    this.setState({
                                        hoverText: '',
                                        hoverZoneName: ''
                                    });
                                }}
                                onClick={e => {
                                    this.setState({
                                        selectedTimeZone: e.target.getAttribute('data-timezone'),
                                        selectedZoneName: e.target.getAttribute('data-zonename')
                                    })
                                    this.getSelectedString();
                                }}
                            />
                        )
                    })
                }
            </svg>
        )
    }
    handleQuickLink = (e, ql) => {
        this.setState({
            selectedTimeZone: ql.value == ql.timezone ? ql.timezone : '',
            selectedZoneName: ql.zoneName
        })
        this.getSelectedString();
    }

    render() {
        const {timeZoneList, generateWorldMap} = this;
        const {hoverText, quickLinks, selectedTimeZone, selectedZoneName} = this.state;
        const {selectBox, showHoverText, showQuickLinks} = this.props;
        return (
            <Grid container spacing={3}>
                <Grid item md={6} sm={12}>
                    {selectBox && timeZoneList()}
                </Grid>
                {showQuickLinks &&
                    (<Grid item md={6} sm={12}>
                        <QuickLinks {...{quickLinks, selectedTimeZone, selectedZoneName}} onClick={this.handleQuickLink} />
                    </Grid>)
                }
                <Grid item md={12} sm={12}>
                    {showHoverText &&
                        <span className="hoverZone">{hoverText}</span>
                    }
                    {generateWorldMap()}
                </Grid>
            </Grid>
        )
    }
}

TimeZoneWorldMap.defaultProps = {
    width: 500,
    height: 250,
    hoverColor: '#5A5A5A',
    selectedColor: '#496A84',
    mapColor: '#BBB',
    defaultCss: 'true',
    localStore: true,
    timezoneList: timezone,
    quickLinks: [{
        "IST": "IST",
        "EAT": "EAT",
        "London": "Europe/London",
        "GMT": "GMT",
        "India": "Asia/Calcutta"
    }],
    showQuickLinks: true,
    selectBox: true,
    showHoverText: true,
    dayLightSaving: ((typeof moment == 'function') ? (true) : (false))
};

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
      justifyContent: 'center',
      flexWrap: 'wrap',
      '& > *': {
        margin: theme.spacing(0.5),
      },
    },
  }));
const QuickLinks = ({quickLinks, selectedTimeZone, selectedZoneName, onClick=null}) => {
    const classes = useStyles();
    return (
        <div className={classes.root}>
            {
                quickLinks && quickLinks.map(ql => (
                        <Chip label={ql.label} key={ql.value} data-select={ql.value}
                            color={(selectedTimeZone == ql.timezone || (ql.value != ql.timezone && selectedZoneName == ql.zoneName)) ? 'primary' : 'default' }
                            onClick={onClick && (e => onClick(e, ql))}
                        />
                    )
                )
            }
        </div>
    )
}

export default TimeZoneWorldMap;
export {TZ, getTimeZoneObj}