import React, {Component} from 'react';
import {observer} from "mobx-react";

import {Grid, Typography, Card, CardContent, Chip, Tooltip, Divider} from '@material-ui/core';
import BallotIcon from '@material-ui/icons/Ballot';
import CardHeader from '@material-ui/core/CardHeader';
import CardActions from '@material-ui/core/CardActions';

import f from 'common-ui/utils/f';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import {configProperties} from 'utils/config_properties';
import {DEPLOYMENT_TYPE} from 'utils/globals';

@observer
class VAIApplications extends Component {
    render() {
        const {data, permission, handleApplicationEdit, handleDeleteApplication} = this.props;

        return (
            <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                <Grid container spacing={3}>
                    {
                        f.models(data).map(app => {
                            const isSelfManaged = app.deploymentType ===DEPLOYMENT_TYPE.SELF_MANAGED.VALUE;
                            const chipLabel = <Typography variant='caption' style={{color: "black"}} >{DEPLOYMENT_TYPE.SELF_MANAGED.LABEL}</Typography>;
                            const truncatedDescription = app.description ? (app.description.length > 470 ? `${app.description.slice(0, 470)}...` : app.description) : '';

                            return (
                                <Grid item xs={12} sm={6}
                                    key={app.id}
                                    className="pointer"
                                    onClick={e => handleApplicationEdit(app.id)}
                                    data-testid="app-card-grid"
                                    data-track-id="application"
                                >
                                    <Card data-testid="app-card" className="adjust-ai-application-cards">
                                        <CardHeader
                                            className="display-block"
                                            title={
                                                <>
                                                    <Typography variant="h6" className='ellipsize-ai-application-title align-title-top text-primary' data-testid="app-name" component="div">
                                                        {app.name}
                                                    </Typography>
                                                    <div className="align-title-top">
                                                        {
                                                            configProperties.isShieldConfigEnable() && isSelfManaged &&
                                                            <Tooltip title="Storing audits on <yourcompany> cloud via self managed configuration by user ADMIN" arrow placement='top'>
                                                                <Chip 
                                                                    size='small'
                                                                    variant="outlined"
                                                                    color="primary"
                                                                    icon={<BallotIcon fontSize='small'/>}
                                                                    label={chipLabel}
                                                                />
                                                            </Tooltip>

                                                        }
                                                    </div>
                                                </>
                                            }
                                        />
                                        <CardContent className='ai-application-card-content'>
                                            <Typography className='break-word' variant="body2" color="textSecondary" component="p"
                                                data-testid="app-desc"
                                            >
                                                {truncatedDescription.length > 470 ? (
                                                    <Tooltip arrow placement="top" title={app.description}>
                                                        <span>{truncatedDescription}</span>
                                                    </Tooltip>
                                                ) : (
                                                    <span>{truncatedDescription}</span>
                                                )}
                                            </Typography>
                                        </CardContent>
                                        <Divider light />
                                        <CardActions className='text-center d-flex-col'>     
                                           <ActionButtonsWithPermission
                                                color="secondary"
                                                data-testid="app-delete-btn"
                                                permission={permission}
                                                hideEdit={true}
                                                onDeleteClick={e => {
                                                    e.stopPropagation();
                                                    handleDeleteApplication(app)
                                                }}
                                            />
                                        </CardActions>
                                    </Card>
                                </Grid>
                            )
                        })
                    }
                </Grid>
            </Loader>
        );
    }
}

export default VAIApplications;