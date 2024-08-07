import React, { Fragment } from 'react';
import { observer } from 'mobx-react';

// Material Imports
import Grid from '@material-ui/core/Grid';
import Tooltip from '@material-ui/core/Tooltip';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import IconButton from '@material-ui/core/IconButton';
import TrendingUpIcon from '@material-ui/icons/TrendingUp';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { Divider } from '@material-ui/core';

import f from 'common-ui/utils/f';

const Ibox = ({ title, headerProps={}, className = "", iboxContentClass = "", children, divider=false, identifier="card-section"}) => {
    return (
        <Card className={className} data-testid={identifier}>
            {title &&
                <CardHeader title={title}
                    titleTypographyProps={{variant: 'body1', component: 'h5'}}
                    {...headerProps}
                />
            }
            {divider && <Divider />}
            {children && <CardContent className={iboxContentClass}>{children}</CardContent>}
        </Card>
    )
}

const FloatMargin = ({ colAttr, title = "", titleIcon = "", children }) => {
    let icon = titleIcon ? <TrendingUpIcon fontSize='small' className="m-r-xs" /> : null;

    return (
        <Grid item {...colAttr}>
            <div className="float-e-margins">
                <div className="file-manager">
                    <Typography variant='subtitle1'>{icon}{title}</Typography>
                    {children}
                </div>
            </div>
        </Grid>
    )
};
FloatMargin.defaultProps = {
    colAttr: { md: 3, sm: 12, xs: 3 }
}

const IBoxMetrics = ({ title = '', colAttr = { xs: 12, sm: 6, md: 4, lg: 4 }, contentProps = {}, count = 0, label = '', textColour = '' }) => {
    if (label === 'HIGH') {
        textColour = 'text-high';
    }
    if (label === 'MEDIUM') {
        textColour = 'text-medium';
    }
    if (label === 'LOW') {
        textColour = 'text-low';
    }
    return (
        <Grid item {...colAttr}>
            <Card>
                {title &&
                    <CardHeader
                        title={title}
                    />
                }
                <CardContent>
                    <Typography align="center" variant="h4" component="h4" gutterBottom display="block" color="textSecondary">
                        {count}
                    </Typography>
                    <Typography align="center" variant="body2" display="block">
                        {label}
                    </Typography>
                </CardContent>
            </Card>
        </Grid>
    )
}

const PanelBody = ({ children, className = '', cardProps = {}, ...props }) => {
    return (
        <Fragment>
            <Card {...cardProps}>
                <CardContent style={{ marginBottom: '0px' }} className={className} {...props}>{children}</CardContent>
            </Card>
        </Fragment>
    )
}

const UnorderedList = observer(function UnorderedList({ data, attr = "", onClick = null, selected = 1 }) {
    let models;
    if (f.isPromise(data)) {
        models = f.models(data).slice();
    } else {
        models = data;
    }
    if (!models || !Array.isArray(models)) {
        return null;
    }
    let list = models.map((d, i) => (
            <Item key={i} active={d.id == selected} onClick={() => onClick && onClick(d, i)}>
                <Typography variant="body2" noWrap color={d.id == selected ? "primary" : "inherit"}>
                    {d[attr]}   
                </Typography>
            </Item>
        )
    )
    return (
        <List className="list-scroller">
            {list}
        </List>
    )
});

const Item = ({ active = false, children, onClick = null }) => {
    return (
        <ListItem button selected={active} onClick={onClick} className={active ? "active space-between" : "space-between"}>{children}</ListItem>
    )
}

const CountWidget = ({ label = "", count = 0, desc = '' , iconColor, iconSize}) => {
    return (
        <Box>
            <Box display="flex" alignItems="center" justifyContent="center" mb={1.5}>
                <Typography component="p" className="m-b-none" align="center" display="block" variant="caption" color="textSecondary" paragraph>{label}
                </Typography>
                <Tooltip arrow id={`tooltip-top`} title={<Typography variant="body2">{desc}</Typography>} placement="top">
                    <IconButton size="small">
                        <InfoOutlinedIcon color={iconColor} style={{fontSize: '14px'}}/>
                    </IconButton>
                </Tooltip>
            </Box>
            <Typography align="center" variant="h4" style={{fontSize: '30px'}} color="textSecondary">{count}</Typography>
        </Box>
    )
}

export {
    Ibox,
    IBoxMetrics,
    PanelBody,
    UnorderedList,
    Item,
    CountWidget,
    FloatMargin
}