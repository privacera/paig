import React, { Component, Fragment } from 'react';
import {reaction} from 'mobx';

import DoneIcon from '@material-ui/icons/Done';
import ClearIcon from '@material-ui/icons/Clear';
import {Grid, Box, Typography, Table, TableBody, TableCell, 
    TableContainer, TableHead, TableRow, Accordion, AccordionDetails, AccordionSummary,
    Tabs, Tab
} from '@material-ui/core';
import ChatIcon from '@material-ui/icons/Chat';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import KeyboardTabIcon from '@material-ui/icons/KeyboardTab';
import SubdirectoryArrowRightIcon from '@material-ui/icons/SubdirectoryArrowRight';

import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
//import { Checkbox } from 'common-ui/components/filters';
import {DATE_TIME_FORMATS, STATUS} from 'common-ui/utils/globals';
import {CommandDisplay} from 'common-ui/components/action_buttons';
import { TabPanel } from 'common-ui/components/generic_components';
import {MESSAGE_RESULT_TYPE, PROMPT_REPLY_TYPE} from 'utils/globals';
import TraitChipList from 'components/audits/security/v_trait_chips';
import VAIApplicationAccessContentRestriction from 'components/policies/v_ai_application_access_content_restriction';
import VVectorDBAccessContentRestriction from 'components/policies/v_vector_db_access_content_restriction';

class VSensitiveDataAccessed extends Component { 
    constructor(props){
        super(props);

        const { data, selectedModel } = this.props;

        const expanded = {};
        const lastIndex = data.length - 1;
        let allExpanded = true;

        data.forEach((model, index) => {
            expanded[index] = (index === 0 && model.requestType === PROMPT_REPLY_TYPE.PROMPT) ||
                (index === lastIndex && model.requestType === PROMPT_REPLY_TYPE.REPLY) ||
                model.id === selectedModel.id;
            if (!expanded[index]) {
                allExpanded = false;
            }
        });

        this.state = {
            expanded,
            allExpanded,
            expandedRows: []
        };
    }

    handleExpandAll = () => {
        const { data } = this.props;
        const { allExpanded } = this.state;

        const expanded = {};
        data.forEach((m, i) => {
            expanded[i] = !allExpanded;
        });

        this.setState({
            allExpanded: !allExpanded,
            expanded
        });
    };
    
    handleAccordionChange = (index) => {
        const {expanded} = this.state;
        expanded[index] = !expanded[index];
        this.setState({
            expanded,
            allExpanded: Object.values(expanded).every((value) => value)
        })
    };

    render() {
        const { selectedModel, data, highlightWordsInBrackets, capitalizeFirstLetter, policyIdPolicyMap, vectorDBPolicyIdPolicyMap} = this.props;
        const {expanded, allExpanded} = this.state;
        let dataLength = data.length;

        if(!dataLength){
            return (
                <div>
                    No data available
                </div>
            )
        };

        return (
            <Fragment>
                <div className='audit-modal-floater'>
                    <div className="audit-header-annotations p-b-10">
                        <div>
                            <span>{`User:`} <span className="content-heading">{`${selectedModel.userId}`}</span> {`Application:`} <span  className="content-heading">{`${selectedModel.applicationName}`}</span>  {`Result:`} </span>
                            {
                                (selectedModel.isMasked || selectedModel.isAllowed) ?
                                <Typography variant="body2" component="span" style={{ color: selectedModel.isMasked ? '#0A84F7' : '#0F9956'}}>
                                    {selectedModel.isMasked ? MESSAGE_RESULT_TYPE.MASKED.LABEL : MESSAGE_RESULT_TYPE.ALLOWED.LABEL}
                                </Typography> :
                                <Typography variant="body2" component="span" style={{ color: '#f50057'}}>
                                    {MESSAGE_RESULT_TYPE.DENIED.LABEL}
                                </Typography>
                            }
                        </div>
                        <div>
                            {/* <Checkbox
                                size="small"
                                // inputProps={{ 'aria-labelledby': labelId }}
                                // checked={checked}
                                disableRipple
                            />
                            <span>Annotation</span> */}
                            <span
                                style={{color: '#0A84F7'}} 
                                className="pointer m-l-sm"
                                onClick={this.handleExpandAll}
                                data-testid="expand-collapse-button"
                            >
                                {allExpanded ? 'Collapse All' : 'Expand All'}
                            </span>
                        </div>
                    </div>
                </div>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <div className='prompt-audit-container'>
                            {
                                data.map((model, modelIndex) => {
                                    let panelClass = 'audit-panel-padding-left p-t-0';
                                    if (model.requestType === PROMPT_REPLY_TYPE.ENRICH_PROMPT || model.requestType === PROMPT_REPLY_TYPE.RAG) {
                                        panelClass = `${panelClass} accordion-row`;
                                    } else if (model.requestType === PROMPT_REPLY_TYPE.REPLY) {
                                        panelClass = `${panelClass} grey-color-class`;
                                    }
                                    const isSelectedModel = selectedModel.threadSequenceNumber === model.threadSequenceNumber;
                                    const rowHighlightClass = isSelectedModel && dataLength > 1 ? 'selected-model-row' : '';

                                    return (
                                        <Accordion
                                            id={isSelectedModel ? "selectedRow" : ""}
                                            key={model.id}
                                            expanded={expanded[modelIndex] || allExpanded}
                                            onChange={() => this.handleAccordionChange(modelIndex)}
                                            className={`${panelClass} ${rowHighlightClass}`}
                                            data-testid={`accordion-${model.id}`}
                                        >
                                            <AuditAccordionSummary
                                                model={model}
                                                capitalizeFirstLetter={capitalizeFirstLetter}
                                            />
                                            <AuditAccordionDetail
                                                accordionDetailProps={{
                                                    className: `${panelClass} ${rowHighlightClass}`
                                                }}
                                                model={model}
                                                highlightWordsInBrackets={highlightWordsInBrackets}
                                                policyIdPolicyMap={policyIdPolicyMap}
                                                vectorDBPolicyIdPolicyMap={vectorDBPolicyIdPolicyMap}
                                            />
                                        </Accordion>
                                    )
                                })
                            }
                        </div>
                    </Grid>
                </Grid>
            </Fragment>
        );
    }
}

const AuditAccordionSummary = ({model, capitalizeFirstLetter}) => {
    return (
        <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1a-content"
            id="panel1a-header"
            style={{ flexDirection: 'row-reverse' }}
            className="access-accordion-row"
        >
            <div className="decrypted-statement">
                <div className="statement-column">
                    {model.requestType === PROMPT_REPLY_TYPE.REPLY && (
                        <KeyboardTabIcon className="color-medium-grey"/>
                    )}
                    {model.requestType === PROMPT_REPLY_TYPE.PROMPT && (
                        <ChatIcon className="color-medium-grey"/>
                    )}
                    {[PROMPT_REPLY_TYPE.ENRICH_PROMPT, PROMPT_REPLY_TYPE.RAG].includes(model.requestType) &&
                        <SubdirectoryArrowRightIcon className="color-medium-grey"/>
                    }
                </div>
                <div className="statement-column statement-type">
                    {model.requestType === PROMPT_REPLY_TYPE.ENRICH_PROMPT ? 'Prompt to LLM' :
                    (model.requestType === PROMPT_REPLY_TYPE.RAG ? 'Context documents' : capitalizeFirstLetter(model.requestType))}
                </div>
                {/* <div className="statement-column statement-prompt-header">
                    Policy ID:
                    {model.paigPolicyIds && model.paigPolicyIds.length > 0 ? (
                        model.paigPolicyIds.map((policyId, index) => (
                        <span key={index} className='m-l-xs'>
                            {policyId}
                            {index !== model.paigPolicyIds.length - 1 ? ', ' : ''}
                        </span>
                        ))
                    ) : (
                        '--'
                    )}
                </div> */}
                <div className="statement-column statement-moment">
                    {`${Utils.dateUtil.getTimeZone(model.eventTime, DATE_TIME_FORMATS.DATE_FORMAT)}`}
                </div>
                <div className="statement-column statememt-component">
                    {
                        (model.isMasked || model.isAllowed)
                        ? <Typography variant="body2" style={{ color: model.isMasked ? '#0A84F7' : '#0F9956' }}>
                            {
                                model.isMasked ? MESSAGE_RESULT_TYPE.MASKED.LABEL : MESSAGE_RESULT_TYPE.ALLOWED.LABEL
                            }
                        </Typography>
                        : <Typography variant="body2" style={{ color: '#f50057' }}>{MESSAGE_RESULT_TYPE.DENIED.LABEL}</Typography>
                    }
                </div>
                {model.context?.vectorDBInfo && (
                    <div className="statement-column">
                        <Typography variant="body2" style={{ color: '#0F9956' }}>
                            VectorDB Filter Applied
                        </Typography>
                    </div>
                )}
                <div className="statement-column">
                    <TraitChipList model={model} />
                </div>
            </div>
        </AccordionSummary>
    )
}

function a11yProps(index) {
  return {
    id: `scrollable-auto-tab-${index}`,
    'aria-controls': `scrollable-auto-tabpanel-${index}`,
    className: 'p-b-0',
    style: {
        minWidth: '90px'
    }
  };
}

class AuditAccordionDetail extends Component {
    state={
        value: 0
    }
    constructor(props) {
        super(props);

        const {model, policyIdPolicyMap, vectorDBPolicyIdPolicyMap} = this.props;

        this.policyData = f.initCollection();
        this.vectorDbPolicyData = f.initCollection();

        this.policyReaction = reaction(
            () => policyIdPolicyMap.keys(),
            () => {
                let length = model.paigPolicyIds?.length;
                // check if policyIdPolicyMap has all the policyIds from model.paigPolicyIds

                let hasAllIds = model.paigPolicyIds?.every(policyId => policyIdPolicyMap.has(Number(policyId)));

                if (length === 0) {
                    f.resetCollection(this.policyData);
                } else if (length && hasAllIds) {
                    let list = model.paigPolicyIds.map(policyId => policyIdPolicyMap.get(Number(policyId))).filter(Boolean);
                    f.resetCollection(this.policyData, list);
                }
            }
        );

        this.vectorDBPolicyReaction = reaction(
            () => vectorDBPolicyIdPolicyMap.keys(),
            () => {
                let policyIds = model.context?.vectorDBInfo?.vectorDBPolicyInfo || [];
                let length = policyIds.length;

                let hasAllIds = policyIds.every(policy => vectorDBPolicyIdPolicyMap.has(Number(policy.id)));

                if (length === 0) {
                    f.resetCollection(this.vectorDbPolicyData);
                } else if (length && hasAllIds) {
                    let list = policyIds.map(policy => vectorDBPolicyIdPolicyMap.get(Number(policy.id))).filter(Boolean);
                    f.resetCollection(this.vectorDbPolicyData, list);
                }
            }
        );
    }
    componentWillUnmount() {
        this.policyReaction?.();
        this.vectorDBPolicyReaction?.();
        delete this.policyReaction;
        delete this.vectorDBPolicyReaction;
    }
    handleChange = (event, newValue) => {
        this.setState({
            value: newValue
        });
    };
    render() {
        const {model, highlightWordsInBrackets, accordionDetailProps={}, policyIdPolicyMap} = this.props;

        let showTabs = model.paigPolicyIds?.length > 0;
        const {value} = this.state;
        const {handleChange, policyData} = this;

        return (
            <AccordionDetails {...accordionDetailProps}>
                <div className="full-width-with-padding">
                    {
                        showTabs ?
                            <Fragment>
                                <Tabs
                                    indicatorColor="primary"
                                    textColor="primary"
                                    scrollButtons="auto"
                                    variant="scrollable"
                                    className="tabs-view"
                                    value={value}
                                    onChange={handleChange}
                                >
                                    <Tab
                                        label="Details"
                                        {...a11yProps(0)}
                                    />
                                    <Tab
                                        label="Content Restriction"
                                        {...a11yProps(1)}
                                    />
                                    {
                                        model.context?.vectorDBInfo &&
                                        <Tab
                                            label="VectorDB Filtering"
                                            {...a11yProps(2)}
                                        />
                                    }
                                    {
                                        model.context?.vectorDBInfo &&
                                        <Tab
                                            label="VectorDB Filters"
                                            {...a11yProps(3)}
                                        />
                                    }
                                </Tabs>
                                <TabPanel value={value} index={0} px={0} py={1}>
                                    <AuditMsg
                                        model={model}
                                        highlightWordsInBrackets={highlightWordsInBrackets}
                                    />
                                </TabPanel>
                                <TabPanel value={value} index={1} px={0} py={1}>
                                    <VAIApplicationAccessContentRestriction
                                        cPolicies={policyData}
                                        showStatusColumn={false}
                                    />
                                </TabPanel>
                                {
                                    model.context?.vectorDBInfo &&
                                    <Fragment>
                                        <TabPanel value={value} index={2} px={0} py={1}>
                                            <VVectorDBAccessContentRestriction
                                                cPolicies={this.vectorDbPolicyData}
                                                showStatusColumn={false}
                                            />
                                        </TabPanel>
                                        <TabPanel value={value} index={3} px={0} py={1}>
                                            <VectorDBFilter vectorDBInfo={model.context?.vectorDBInfo} />
                                        </TabPanel>
                                    </Fragment>
                                }
                            </Fragment>
                        :
                            <Fragment>
                                <VectorDBFilter vectorDBInfo={model.context?.vectorDBInfo} />
                                <AuditMsg
                                    model={model}
                                    highlightWordsInBrackets={highlightWordsInBrackets}
                                />
                            </Fragment>
                    }
                </div>
            </AccordionDetails>
        )
    }
}

const AuditMsg = ({model, highlightWordsInBrackets}) => {
  let messages = model.messages || [];
  return (
    <Fragment>
      {
        messages.map((message, index) => {
          let maskedMessage = message.decryptedMaskedMessage || message.decryptedMessage || message.maskedMessage;
          if (model.isMasked && maskedMessage) {
            maskedMessage = highlightWordsInBrackets(maskedMessage);
          }

          return (
            <Box key={index} component="pre" p={1} borderRadius="6px" className="audit-content-padding">
              {message.decryptedMessage || message.originalMessage || "--"}
              {
                maskedMessage && maskedMessage !== message.decryptedMessage && maskedMessage !== message.decryptedMaskedMessage &&
                <Box
                  className="audit-response-padding"
                  component="pre"
                  p={1}
                  borderRadius="6px"
                  marginTop="5px"
                  style={{ background: "#EAF3FA" }}
                >
                  <span className='privacera-modified-message'>
                    Content modified by privacera
                  </span>
                  <span>{maskedMessage}</span>
                </Box>
              }
            </Box>
          );
        })
      }
    </Fragment>
  )
}

const VectorDBFilter = ({vectorDBInfo}) => {
    if (!vectorDBInfo) {
        return null;
    }

    return (
        <Fragment>
            <Box component="pre" p={1} borderRadius="6px" className="audit-content-padding">
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell className='min-width-200'>Vector DB Name</TableCell>
                                <TableCell>Filter Applied</TableCell>
                                <TableCell className='min-width-136 word-break text-center'>User/Group Access-Limited Retrieval</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <TableCell>
                                    {vectorDBInfo.vectorDBName || '--'}
                                </TableCell>
                                <TableCell>
                                    {
                                        vectorDBInfo.filterExpression
                                        ? <CommandDisplay id="filter-expression" contentProps={{className: 'break-all'}} command={vectorDBInfo.filterExpression} />
                                        : '--'
                                    }
                                </TableCell>
                                <TableCell className='text-center'>
                                    {
                                        vectorDBInfo.userEnforcement === STATUS.enabled.value
                                        ? <DoneIcon data-testid="vector-db-enabled" className="text-success" />
                                        : <ClearIcon data-testid="vector-db-disabled" color="secondary" />
                                    }
                                </TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>
        </Fragment>
    )
}

export default VSensitiveDataAccessed;