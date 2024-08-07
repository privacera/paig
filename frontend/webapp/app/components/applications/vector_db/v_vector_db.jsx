import React, {Component} from 'react';
import {observer} from "mobx-react";

import {Grid, Typography, Card, CardContent, Divider, Tooltip} from '@material-ui/core';
import CardHeader from '@material-ui/core/CardHeader';
import CardActions from '@material-ui/core/CardActions';

import f from 'common-ui/utils/f';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

@observer
class VVectorDB extends Component {
    render() {
        const {data, permission, handleVectorDBEdit, handleDeleteVectorDB} = this.props;

        return (
            <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                <Grid container spacing={3}>
                    {
                        f.models(data).map(model => {
                            const truncatedDescription = model.description ? (model.description.length > 470 ? `${model.description.slice(0, 470)}...` : model.description) : '';

                            return (
                                <Grid item xs={12} sm={6}
                                    key={model.id}
                                    className="pointer"
                                    onClick={e => handleVectorDBEdit(model.id)}
                                    data-testid="card-grid"
                                    data-track-id="vector-db-grid"
                                >
                                    <Card data-testid="card" className="adjust-ai-application-cards">
                                        <CardHeader
                                            className="display-block"
                                            title={
                                                <Typography variant="h6" className="ellipsize-ai-application-title text-primary" data-testid="name" component="div">
                                                    {model.name}
                                                </Typography>
                                            }
                                        />       
                                        <CardContent className='ai-application-card-content'>
                                            <Typography className='break-word' variant="body2" color="textSecondary" component="p"
                                                data-testid="desc"
                                            >
                                                {truncatedDescription.length > 470 ? (
                                                    <Tooltip arrow placement="top" title={model.description}>
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
                                                data-testid="delete-btn"
                                                permission={permission}
                                                hideEdit={true}
                                                onDeleteClick={e => {
                                                    e.stopPropagation();
                                                    handleDeleteVectorDB(model)
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

export default VVectorDB;