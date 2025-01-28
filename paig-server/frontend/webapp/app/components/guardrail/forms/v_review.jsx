import React, {Fragment} from 'react';

import {
    Grid, Typography, Chip, Box, Paper, Button, Slider,
    TableContainer, Table, TableHead, TableBody, TableRow, TableCell
} from '@material-ui/core';
import {Alert} from '@material-ui/lab';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';

import {GUARDRAIL_PROVIDER, GUARDRAIL_CONFIG_TYPE} from 'utils/globals';
import {FormHorizontal, FormGroupInput} from 'common-ui/components/form_fields';
import {content_moderation_list} from 'components/guardrail/forms/content_moderation_list';

const HeaderWithEditButton = ({title, i, step, onEditClick, containerProps={}}) => {
    return (
        <Fragment>
            <Grid container spacing={3} {...containerProps}>
                <Grid item xs={10}>
                    <Typography variant="h6">
                        {title}
                    </Typography>
                </Grid>
                {
                    onEditClick &&
                    <Grid item xs={2}>
                        <Button
                            variant="outlined"
                            color="primary"
                            size="small"
                            className="pull-right"
                            data-testid="edit-button"
                            onClick={() => onEditClick(step, i)}
                        >
                            EDIT
                        </Button>
                    </Grid>
                }
            </Grid>
        </Fragment>
    )
}

const VBasicInfo = ({formUtil, data, stepConfig, i, onEditClick}) => {
    let guardrailProvider = Object.values(GUARDRAIL_PROVIDER).find(p => p.NAME === data.guardrailProvider);

    const error = formUtil.getErrors();

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'basic-info'
                }}
            />
            <Grid container spacing={3}>
                {
                    (error.basicInfo?.name) &&
                    <Grid item xs={12}>
                        <Alert severity="error" data-testid="guardrail-basic-alert">
                            {error.basicInfo.name}
                        </Alert>
                    </Grid>
                }
                <FormGroupInput
                    label="Name"
                    value={data.name}
                    textOnly={true}
                />
                <FormGroupInput
                    as="textarea"
                    label="Description"
                    value={data.description}
                    textOnly={true}
                />
            </Grid>
            <hr />
            <Grid container spacing={3} className="m-b-sm">
                <Grid item xs={12}>
                    <Typography variant="h6">
                        Connected Guardrails
                    </Typography>
                </Grid>
            </Grid>
            {
                error.basicInfo?.guardrailConnections &&
                <Grid item xs={12}>
                    <Alert severity="error">
                        {error.basicInfo.guardrailConnections}
                    </Alert>
                </Grid>
            }
            <Grid container spacing={3} className="m-b-sm">
                <Grid item xs={12} sm="auto" className="border-radius-5 card-border-grey m-b-sm m-l-sm m-r-xs" style={{minWidth: '48%'}}>
                    <Grid container>
                        {
                            GUARDRAIL_PROVIDER.PAIG.IMG_URL &&
                            <Grid item className="m-r-sm">
                                <div style={{
                                     width: '40px',
                                     height: '40px',
                                     backgroundColor: '#eaf3fa',
                                     display: 'flex',
                                     justifyContent: 'center',
                                     alignItems: 'center'
                                }}>
                                    <img
                                        className={"services-logo " + GUARDRAIL_PROVIDER.PAIG.NAME}
                                        src={GUARDRAIL_PROVIDER.PAIG.IMG_URL}
                                        alt="service-logo"
                                        style={{
                                            width: 'auto',
                                            height: '30px'
                                        }}
                                    />
                                </div>
                            </Grid>
                        }
                        <Grid item>
                            <Typography variant="subtitle2">{GUARDRAIL_PROVIDER.PAIG.LABEL}</Typography>
                            <Chip
                                size="small"
                                label="Always Enabled"
                            />
                        </Grid>
                    </Grid>
                </Grid>
                {
                    guardrailProvider &&
                    <Grid item xs={12} sm="auto" className="border-radius-5 card-border-grey m-b-sm m-l-sm m-r-xs" style={{minWidth: '48%'}}>
                        <Grid container>
                            {
                                guardrailProvider.IMG_URL &&
                                <Grid item className="m-r-sm">
                                    <div style={{
                                         width: '40px',
                                         height: '40px',
                                         backgroundColor: '#eaf3fa',
                                         display: 'flex',
                                         justifyContent: 'center',
                                         alignItems: 'center'
                                    }}>
                                        <img
                                            className={"services-logo " + guardrailProvider.NAME}
                                            src={guardrailProvider.IMG_URL}
                                            alt="service-logo"
                                            style={{
                                                width: 'auto',
                                                height: '30px'
                                            }}
                                        />
                                    </div>
                                </Grid>
                            }
                            <Grid item>
                                <Typography variant="subtitle2">{guardrailProvider.LABEL}</Typography>
                                <Typography variant="body2">Connection: {data.guardrailConnectionName}</Typography>
                            </Grid>
                        </Grid>
                    </Grid>
                }
            </Grid>
        </Fragment>
    )
}

const VContentModeration = ({data, formUtil, stepConfig, i, onEditClick}) => {
    let contentModeration = formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.CONTENT_MODERATION.NAME) || {};
    const { status, configData={} } = contentModeration;

    let enabled = true;
    if (!status) {
        enabled = false
    }

    let categorySelected = configData.configs?.reduce((acc, config) => {
        acc.push(config.category);
        return acc;
    }, []) || [];

    let missingList = content_moderation_list.filter(c => c.providers.includes(data.guardrailProvider)).filter(c => !categorySelected.includes(c.category));

    const error = formUtil.getErrors();

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title + (enabled ? '' : ' (Disabled)')}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'content-moderation-header'
                }}
            />
            {
                enabled &&
                <Fragment>
                    {
                        error.contentModerationFilters?.contentModeration &&
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Alert severity="error" data-testid="content-moderation-alert">
                                    {error.contentModerationFilters.contentModeration}
                                </Alert>
                            </Grid>
                        </Grid>
                    }
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                           <TableContainer>
                               <Table className="table-header-bg" data-testid="table">
                                   <TableHead data-testid="thead">
                                       <TableRow className="grey-bg">
                                           <TableCell>Category</TableCell>
                                           <TableCell>Description</TableCell>
                                           <TableCell>Filter Strength Prompt</TableCell>
                                           <TableCell>Filter Strength Reply</TableCell>
                                       </TableRow>
                                   </TableHead>
                                   <TableBody data-testid="tbody">
                                       {
                                           configData.configs.map(config => {
                                               return (
                                                   <TableRow className="table-search-row" key={config.category}>
                                                        <TableCell>{config.category}</TableCell>
                                                        <TableCell></TableCell>
                                                        <TableCell>{config.filterStrengthPrompt}</TableCell>
                                                        <TableCell>{config.filterStrengthResponse}</TableCell>
                                                   </TableRow>
                                               )
                                           })
                                       }
                                       {
                                           missingList.length > 0 &&
                                            <TableRow className="table-search-row">
                                                <TableCell colSpan={4} className="text-center">
                                                    {missingList.length} category not selected
                                                    </TableCell>
                                            </TableRow>
                                       }
                                    </TableBody>
                               </Table>
                           </TableContainer>
                        </Grid>
                    </Grid>
                </Fragment>
            }
        </Fragment>
    )
}

const VSensitiveDataFilters = ({formUtil, stepConfig, i, onEditClick}) => {
    const data = formUtil.getData();
    let sensitiveData = formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.SENSITIVE_DATA.NAME) || {};
    let elements = sensitiveData.configData?.configs?.filter(c => c.category) || [];
    let regex = sensitiveData.configData?.configs?.filter(c => c.type === 'regex') || [];

    const { status, configData } = sensitiveData;

    const error = formUtil.getErrors();

    let enabled = true;
    if (!status) {
        enabled = false
    }

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title + (enabled ? '' : ' (Disabled)')}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'sensitive-data-header'
                }}
            />
            {
                enabled &&
                <Fragment>
                    {
                        error.sensitiveDataFilters?.sensitiveData &&
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Alert severity="error" data-testid="sensitive-data-alert">
                                    {error.sensitiveDataFilters.sensitiveData}
                                </Alert>
                            </Grid>
                        </Grid>
                    }
                    <Typography variant="body1" className="m-t-sm" data-testid="sensitive-data-element-header">Elements</Typography>
                    <Grid container spacing={3} className="m-b-md" data-testid="sensitive-data-element-table">
                        <Grid item xs={12}>
                           <TableContainer>
                               <Table className="table-header-bg" data-testid="table">
                                   <TableHead data-testid="thead" className="grey-bg">
                                       <TableRow>
                                           <TableCell>Name</TableCell>
                                           <TableCell>Description</TableCell>
                                           <TableCell>Action</TableCell>
                                       </TableRow>
                                   </TableHead>
                                   <TableBody data-testid="tbody">
                                       {
                                           elements.length > 0
                                           ?
                                               elements.map(config => {
                                                   return (
                                                       <TableRow className="table-search-row" key={config.category}>
                                                            <TableCell>{config.category}</TableCell>
                                                            <TableCell></TableCell>
                                                            <TableCell>{config.action}</TableCell>
                                                       </TableRow>
                                                   )
                                               })
                                           :
                                               <TableRow className="table-search-row">
                                                    <TableCell colSpan={3}>No elements added</TableCell>
                                               </TableRow>
                                       }
                                    </TableBody>
                               </Table>
                           </TableContainer>
                        </Grid>
                    </Grid>
                    {
                        (data.guardrailProvider && data.guardrailProvider !== GUARDRAIL_PROVIDER.PAIG.NAME) &&
                        <Fragment>
                            <Typography variant="body1" className="m-t-sm" data-testid="sensitive-data-regex-header">Regex</Typography>
                            <Grid container spacing={3} data-testid="sensitive-data-regex-table">
                                <Grid item xs={12}>
                                   <TableContainer>
                                       <Table className="table-header-bg" data-testid="table">
                                           <TableHead data-testid="thead" className="grey-bg">
                                               <TableRow>
                                                   <TableCell>Name</TableCell>
                                                   <TableCell>Pattern</TableCell>
                                                   <TableCell>Description</TableCell>
                                                   <TableCell>Action</TableCell>
                                               </TableRow>
                                           </TableHead>
                                           <TableBody data-testid="tbody">
                                               {
                                                   regex.length > 0
                                                   ?
                                                       regex.map(config => {
                                                           return (
                                                               <TableRow className="table-search-row" key={config.name}>
                                                                    <TableCell>{config.name}</TableCell>
                                                                    <TableCell>{config.pattern}</TableCell>
                                                                    <TableCell>{config.description}</TableCell>
                                                                    <TableCell>{config.action}</TableCell>
                                                               </TableRow>
                                                           )
                                                       })
                                                   :
                                                       <TableRow className="table-search-row">
                                                           <TableCell colSpan={4}>No regex added</TableCell>
                                                       </TableRow>
                                               }
                                           </TableBody>
                                       </Table>
                                   </TableContainer>
                                </Grid>
                            </Grid>
                        </Fragment>
                    }
                </Fragment>
            }
        </Fragment>
    )
}

const VOffTopicFilters = ({formUtil, stepConfig, i, onEditClick}) => {
    let offTopics = formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.OFF_TOPIC.NAME) || {};
    const { status, configData={} } = offTopics;

    let enabled = true;
    if (!status) {
        enabled = false
    }

    const error = formUtil.getErrors();

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title + (enabled ? '' : ' (Disabled)')}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'off-topic-header'
                }}
            />
            {
                enabled &&
                <Fragment>
                    {
                        error.offTopicFilters?.offTopic &&
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Alert severity="error" data-testid="off-topic-alert">
                                    {error.offTopicFilters.offTopic}
                                </Alert>
                            </Grid>
                        </Grid>
                    }
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                           <TableContainer>
                               <Table className="table-header-bg" data-testid="table">
                                   <TableHead data-testid="thead">
                                       <TableRow className="grey-bg">
                                           <TableCell>Topic</TableCell>
                                           <TableCell>Definition</TableCell>
                                           <TableCell>Sample Phrases</TableCell>
                                           <TableCell>Actions</TableCell>
                                       </TableRow>
                                   </TableHead>
                                   <TableBody data-testid="tbody">
                                       {
                                           configData.configs?.length > 0
                                           ?
                                               configData.configs.map(config => {
                                                   let samplePhrases = config.samplePhrases?.join('\n');
                                                   return (
                                                       <TableRow className="table-search-row" key={config.category}>
                                                            <TableCell>{config.topic}</TableCell>
                                                            <TableCell>{config.definition}</TableCell>
                                                            <TableCell>
                                                                <FormGroupInput
                                                                    as="textarea"
                                                                    showLabel={false}
                                                                    disabled={true}
                                                                    variant="standard"
                                                                    rows={1}
                                                                    InputProps={{disableUnderline: true, maxRows: 4}}
                                                                    value={samplePhrases}
                                                                />
                                                            </TableCell>
                                                            <TableCell>{config.action}</TableCell>
                                                       </TableRow>
                                                   )
                                               })
                                           :
                                                 <TableRow className="table-search-row">
                                                     <TableCell colSpan={4}>No off topics found</TableCell>
                                                 </TableRow>
                                       }
                                    </TableBody>
                               </Table>
                           </TableContainer>
                        </Grid>
                    </Grid>
                </Fragment>
            }
        </Fragment>
    )
}

const VDeniedTerms = ({formUtil, stepConfig, i, onEditClick}) => {
    let deniedTerms = formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.DENIED_TERMS.NAME) || {};

    const { status, configData={} } = deniedTerms;

    let enabled = true;
    if (!status) {
        enabled = false
    }

    let nonProfanity = configData.configs?.filter(c => c.type !== 'PROFANITY') || [];
    let profanity = configData.configs?.filter(c => c.type === 'PROFANITY').map(c => c.value).join('') === 'true' ? <span><CheckCircleIcon fontSize="small" color="primary" /> Enabled</span> : 'Disabled'

    const error = formUtil.getErrors();

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title + (enabled ? '' : ' (Disabled)')}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'denied-terms-header'
                }}
            />
            {
                enabled &&
                <Fragment>
                    {
                        error.deniedTermsFilters?.deniedTerms &&
                        <Grid container spacing={3} className="m-b-xs">
                            <Grid item xs={12}>
                                <Alert severity="error" data-testid="denied-terms-alert">
                                    {error.deniedTermsFilters.deniedTerms}
                                </Alert>
                            </Grid>
                        </Grid>
                    }
                    <Grid container spacing={3}>
                        <Grid item xs={12} data-testid="profanity-filter">
                            Profanity blocking: {profanity}
                        </Grid>
                    </Grid>
                    {
                        nonProfanity && nonProfanity.length > 0 &&
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                               <TableContainer>
                                   <Table className="table-header-bg" data-testid="table">
                                       <TableHead data-testid="thead">
                                           <TableRow className="grey-bg">
                                               <TableCell>Terms</TableCell>
                                               <TableCell>Phrases and keywords</TableCell>
                                           </TableRow>
                                       </TableHead>
                                       <TableBody data-testid="tbody">
                                           {
                                               nonProfanity.length > 0
                                               ?
                                                   nonProfanity.map(config => {
                                                       return (
                                                           <TableRow className="table-search-row" key={config.term}>
                                                                <TableCell>{config.term}</TableCell>
                                                                <TableCell>{config.keywords?.join(', ') || '--'}</TableCell>
                                                           </TableRow>
                                                       )
                                                   })
                                               :
                                                    <TableRow className="table-search-row">
                                                        <TableCell colSpan={2}>No denied terms found</TableCell>
                                                    </TableRow>
                                           }
                                        </TableBody>
                                   </Table>
                               </TableContainer>
                            </Grid>
                        </Grid>
                    }
                </Fragment>
            }
        </Fragment>
    )
}

const VPromptSafety = ({formUtil, stepConfig, i, onEditClick}) => {
    let promptSafety = formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.PROMPT_SAFETY.NAME) || {};

    const { status, configData={} } = promptSafety;

    let enabled = true;
    if (!status || !configData.configs?.length) {
        enabled = false
    }

    const promptAttack = configData.configs?.find(c => c.category === 'PROMPT_ATTACK');
    if (!promptAttack) {
        enabled = false
    }

    const marks = [
     {
         value: 0,
         label: 'None'
     },
     {
         value: 33,
         label: 'LOW'
     },
     {
         value: 66,
         label: 'MEDIUM'
     },
     {
         value: 100,
         label: 'HIGH'
     }
  ]

    const value = marks.find(m => m.label === promptAttack?.filterStrengthPrompt)?.value || 0;

    return (
        <Fragment>
            <HeaderWithEditButton
                title={stepConfig.title + (enabled ? '' : ' (Disabled)')}
                step={stepConfig}
                i={i}
                onEditClick={onEditClick}
                containerProps={{
                    'data-testid': 'prompt-safety-header'
                }}
            />
            {
                enabled &&
                <Grid container spacing={3} className="justify-center">
                    <Grid item xs={11} sm={8} style={{paddingLeft: '20px'}}>
                        <Slider
                            value={value}
                            valueLabelFormat={val => `${val}%`}
                            getAriaValueText={val => `${val}%`}
                            aria-labelledby="prompt attack sensitivity"
                            step={null}
                            valueLabelDisplay="auto"
                            marks={marks}
                        />
                    </Grid>
                </Grid>
            }
        </Fragment>
    )
}

const reviewComponent = {
    VBasicInfo,
    VContentModeration,
    VSensitiveDataFilters,
    VOffTopicFilters,
    VDeniedTerms,
    VPromptSafety
}

const VReview = ({formUtil, onStepClick}) => {
    let steps = formUtil.getSteps().slice(0, -3) || [];
    let data = formUtil.getData();
    return steps.map((stepConfig, i) => {
        if (!(stepConfig && reviewComponent[stepConfig.reviewComponent])) {
            return null;
        }

        const ReviewComponent = reviewComponent[stepConfig.reviewComponent];

        return (
            <Box component={Paper} p="15px" className="m-b-md" key={stepConfig.title}>
                <ReviewComponent
                    i={i}
                    data={data}
                    formUtil={formUtil}
                    stepConfig={stepConfig}
                    onEditClick={onStepClick}
                />
            </Box>
        )
    });
}

export default VReview