import React, { Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';

import Link from '@material-ui/core/Link';
import TableRow from '@material-ui/core/TableRow';
import {TableCell, Typography} from '@material-ui/core';

import ChatIcon from '@material-ui/icons/Chat';
import IconButton from '@material-ui/core/IconButton';
import KeyboardTabIcon from '@material-ui/icons/KeyboardTab';
import SubdirectoryArrowRightIcon from '@material-ui/icons/SubdirectoryArrowRight';

import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import FSModal from 'common-ui/lib/fs_modal';
import Table from 'common-ui/components/table';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {configProperties} from 'utils/config_properties';
import {MESSAGE_RESULT_TYPE, PROMPT_REPLY_TYPE, DEPLOYMENT_TYPE} from 'utils/globals';
import CSensitiveDataAccessed from 'containers/audits/security/c_sensitive_data_accessed';
import TraitChipList from 'components/audits/security/v_trait_chips';

@inject('encryptDecryptStore', 'securityAuditsStore', 'dataProtectStore')
@observer
class Statement extends Component {
    constructor(props){
        super(props);
    }

    handleMessageDisplay = (model) => {
        this.warningModal?.show({
            title: 'Sensitive Data Warning',
            btnOkText: 'Proceed',
            btnCancelText: 'Cancel',
            showDivider: false
        });
    }
    
    handleSensitiveDataView = async () => {
        this.warningModal?.okBtnDisabled(true);
        this.warningModal?.hide();
        
        const {_vState, model, applicationKeyMap} = this.props;

        let app = applicationKeyMap[model.applicationKey];
        if (configProperties.isShieldConfigEnable() && app?.deploymentType === DEPLOYMENT_TYPE.SELF_MANAGED.VALUE) {
            if (_vState.shieldObj?.shieldAuditServerUrl) {
                try {
                    let token = await this.props.dataProtectStore.generateToken();
                    let url = `${_vState.shieldObj.shieldAuditServerUrl}/#/sensitive-data/${model.threadId}/${model.eventTime}?token=${token.jwtToken}`;
                    window.open(url, '_blank');
                } catch(e) {
                    f.handleError()(e);;
                }
            } else {
               f.notifyWarning('Please set Shield Audit Server URL in Shield Configuration');
            }
        } else {
            this.messageModal?.show({
                title: 'Audit Content',
                showOkButton: false
            });
        }
    }
    
    handleMessageDisplayClose = () => {
        this.props.model.showText = false;
        this.messageModal?.hide();
    }
    render() {
        const {model, applicationKeyMap} = this.props;
        const {handleMessageDisplay} = this;

        return (
            <Fragment>
                <span 
                    data-track-id="audits-statement-view-icon" 
                    data-testid="audits-statement-view-icon" 
                >
                    <Link
                        onClick={() => {
                            handleMessageDisplay(model);
                        }}
                    >
                        More Details
                    </Link>
                </span>
                <FSModal  ref={ref => this.warningModal = ref} dataResolve={this.handleSensitiveDataView}>
                    <Typography>
                        You are about to reveal potentially sensitive information.
                        Your action will be logged for both security and compliance purposes.
                        Ensure you're in a private settings to prevent unauthorized viewing. Do you wish to proceed?
                    </Typography>
                </FSModal>
                <FSModal showExpandButton ref={ref => this.messageModal = ref} maxWidth="lg" reject={this.handleMessageDisplayClose}>
                    <CSensitiveDataAccessed
                        selectedModel={model}
                        applicationKeyMap={applicationKeyMap}
                    />
                </FSModal>
            </Fragment>
        )
    }
}

class VSecurityAudits extends Component {
    constructor(props) {
        super(props);
        this.state = {
            expandedRows: []
        };
    }

    capitalizeFirstLetter = (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };

    toggleRow = (threadId) => {
        this.setState((prevState) => {
            const expandedRows = [...prevState.expandedRows];
    
            const index = expandedRows.indexOf(threadId);
            if (index === -1) {
                expandedRows.push(threadId);
            } else {
                expandedRows.splice(index, 1);
            }
    
            return { expandedRows };
        });
    };
    
    getRowSpan = (model, groupedRows, index) => {
        const { expandedRows } = this.state;
        let rowSpan = model.length;
        const ungroupedRows = model.filter((d) => !groupedRows[index]?.includes(d));  
        if (expandedRows.length === 0) {
            return ungroupedRows.length;
        }
        if (!expandedRows.includes(model[0].threadId)) {
            rowSpan = ungroupedRows.length;
        } else if (groupedRows[index]) {
            rowSpan = ungroupedRows.length + 1;
        }
        return rowSpan;
    }
   
    getHeaders = () => {
        let headers = [
            <TableCell width="10px" key="emptyCell"></TableCell>,
            <TableCell width="100px" key="request">Request</TableCell>,
            // <TableCell width="60px" key="policyId">Policy Id</TableCell>,
            <TableCell width="150px" key="evtTime">Event Time</TableCell>,
            <TableCell width="100px" key="user">User</TableCell>,
            <TableCell width="100px" key="application">Application</TableCell>,
            <TableCell width="100px" key="result">Result</TableCell>,
            <TableCell width="150px" key="sensitiveData">Sensitive Data</TableCell>,
            <TableCell width="60px" key="statement" align='center'>Statement</TableCell>
        ];

        return headers;
    }

    getRowData = (model, rowIndex) => {
        const { data, pageChange, _vState, applicationKeyMap} = this.props;
        const { expandedRows } = this.state;

        const rows = [];
        const outerRows = [];
        const groupedRows = {};
        const promptIndex = model.findIndex(d => d.requestType === PROMPT_REPLY_TYPE.PROMPT);
        const replyLastIndex = model.findLastIndex(d => d.requestType === PROMPT_REPLY_TYPE.REPLY);
        const isEnrichedPrompt = model.findIndex(d => d.requestType === PROMPT_REPLY_TYPE.ENRICH_PROMPT);
        const isRagLLM = model.findIndex(d => d.requestType === PROMPT_REPLY_TYPE.RAG);
        const promptOrReplyIsPresent = promptIndex !== -1 || replyLastIndex !== -1;

        model.forEach((d, index) => {
            if (!promptOrReplyIsPresent ) {
                outerRows.push(d);
            } else {
                if (
                    (promptIndex !== -1 && index === promptIndex) ||
                    (replyLastIndex !== -1 && index === replyLastIndex && (model.length - 1 === replyLastIndex)) ||
                    (isEnrichedPrompt === -1 && isRagLLM === -1)

                ) {
                    outerRows.push(d);
                } else {
                    let key = Math.max(0, outerRows.length - 1);
                    if (!groupedRows[key]) {
                        groupedRows[key] = [];
                    }
                    groupedRows[key].push(d);
                }
            }
        });


        outerRows.forEach((d, index) => {
            const isExpanded = expandedRows.includes(d.threadId);
            const className = []
            className.push(...[`table-border-bottom`, `table-row-container`])
            if(index == 0 && rowIndex == 0) {
                className.push(`audit-border-top`)
            }
            if ( index == outerRows.length - 1) {
                className.push(`audit-border-bottom`)
            }
            if (isExpanded && outerRows.length == 1) {
                const index = className.indexOf(`audit-border-bottom`);
                if (index > -1) { 
                    className.splice(index, 1);
                }
            }
            rows.push(
                <TableRow 
                    key={index}
                    className={className.join(" ")}>
                    <TableCell width="10px" key="emptyCell">
                        {
                            groupedRows[index]  &&
                            <IconButton
                                style={{ marginRight: isExpanded ? 0 : '12px' }}
                                className={isExpanded ? 'float-icon expanded-icon' : 'float-icon collapsed-icon'}
                                onClick={() => this.toggleRow(d.threadId)} 
                            >
                                {isExpanded ? <ExpandAuditsIcon className="audit-icon" /> : <ExpandAuditsIcon className="audit-icon" />}
                            </IconButton>
                        }
                        {[PROMPT_REPLY_TYPE.ENRICH_PROMPT, PROMPT_REPLY_TYPE.RAG].includes(d.requestType) &&
                            <SubdirectoryArrowRightIcon className="color-medium-grey"/>
                        }
                        {d.requestType === PROMPT_REPLY_TYPE.REPLY && (
                            <KeyboardTabIcon className="color-medium-grey"/>
                        )}
                        {d.requestType === PROMPT_REPLY_TYPE.PROMPT && (
                            <ChatIcon className="color-medium-grey"/>
                        )}
                    </TableCell>
                    <TableCell width="100px" key="request">
                        {d.requestType === PROMPT_REPLY_TYPE.ENRICH_PROMPT ? 'Prompt to LLM' :
                        (d.requestType === PROMPT_REPLY_TYPE.RAG ? 'Context documents' : this.capitalizeFirstLetter(d.requestType))}
                    </TableCell>
                    {/* <TableCell width="60px" key="policyId">
                        {d.paigPolicyIds && d.paigPolicyIds.length > 0 ? (
                            d.paigPolicyIds.map((policyId, index) => (
                            <span key={index}>
                                {policyId}
                                {index !== d.paigPolicyIds.length - 1 ? ', ' : ''}
                            </span>
                            ))
                        ) : (
                            '--'
                        )}
                    </TableCell> */}
                    <TableCell width="150px" key="evtTime">
                        {d.eventTime ? Utils.dateUtil.getTimeZone(d.eventTime, DATE_TIME_FORMATS.DATE_FORMAT) : '--'}
                    </TableCell>
                    <TableCell width="100px" key="user">
                        {d.userId || '--'}
                    </TableCell>
                    <TableCell width="100px" key="application" className='word-break'>
                        {d.applicationName || d.applicationKey || '--'}
                    </TableCell>
                    <TableCell width="100px" key="result">
                        {
                            (d.isMasked || d.isAllowed) ? (
                                <Typography variant="body2" style={{ color: d.isMasked ? '#0A84F7' : '#0F9956' }}>
                                    {d.isMasked ? MESSAGE_RESULT_TYPE.MASKED.LABEL : MESSAGE_RESULT_TYPE.ALLOWED.LABEL}
                                </Typography>
                            ) : (
                                <Typography variant="body2" style={{ color: '#f50057' }}>
                                    {MESSAGE_RESULT_TYPE.DENIED.LABEL}
                                </Typography>
                            )
                        }
                    </TableCell>
                    <TableCell width="150px" key="sensitiveData"  style={{ borderRight: '1px solid rgba(224, 224, 224, 1)' }}> 
                        <TraitChipList model={d}/>
                    </TableCell>
                        {
                            index == 0 && (
                                <TableCell rowSpan={this.getRowSpan(model, groupedRows, index)} key="statement" align='center'>
                                    <Statement
                                        model={d}
                                        data={data}
                                        _vState={_vState}
                                        applicationKeyMap={applicationKeyMap}
                                        onStatementClick={this.handleStatementClick}
                                    />
                                </TableCell>
                            )
                        }
                </TableRow>
            );

            if (groupedRows[index]) {
                rows.push(
                    <SecurityTablePanel llmModel={groupedRows[index]} expandedRows={this.state.expandedRows} pageChange={pageChange} isLastRow={index == outerRows.length - 1}/>
                );
            }
        });
        return rows;
    }
    handleContextMenuSelection = () => {}

    render() {
        const { data, pageChange, _vState } = this.props;
        return (
            <Table
                data={data}
                _vState={_vState}
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
                isRowCustom={true}
                pageChange={pageChange}
                showContextMenu={false}
                onContextMenuSelection={this.handleContextMenuSelection}
                resizable={false}
                tableId="security_audit"
                tableRowAttr={{className: "table-border-bottom"}}
                pagerComponent={true}
                pagination={true}
            />
        )
    }
}

@observer
class SecurityTablePanel  extends Component {
    constructor(props) {
        super(props);
    }
    capitalizeFirstLetter = (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };
    rows = (d, index) => {
    const { expandedRows } = this.props;
    const isExpanded = expandedRows.includes(d.threadId);
    return ([
        <TableRow key={index} className={`table-border-bottom table-row-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
            <TableCell width="10px" key="emptyCell">
                {d.requestType === PROMPT_REPLY_TYPE.REPLY && (
                    <KeyboardTabIcon className="color-medium-grey"/>
                )}
                {d.requestType === PROMPT_REPLY_TYPE.PROMPT && (
                    <ChatIcon />
                )}
                {[PROMPT_REPLY_TYPE.ENRICH_PROMPT, PROMPT_REPLY_TYPE.RAG].includes(d.requestType) &&
                    <SubdirectoryArrowRightIcon className="color-medium-grey"/>
                }
            </TableCell>
            <TableCell width="100px" key="request">
                {d.requestType === PROMPT_REPLY_TYPE.ENRICH_PROMPT ? 'Prompt to LLM' :
                (d.requestType === PROMPT_REPLY_TYPE.RAG ? 'Context documents' : this.capitalizeFirstLetter(d.requestType))}
            </TableCell>
            {/* <TableCell width="60px" key="policyId">
                {d.paigPolicyIds && d.paigPolicyIds.length > 0 ? (
                    d.paigPolicyIds.map((policyId, index) => (
                    <span key={index}>
                        {policyId}
                        {index !== d.paigPolicyIds.length - 1 ? ', ' : ''}
                    </span>
                    ))
                ) : (
                    '--'
                )}
            </TableCell> */}
            <TableCell width="150px" key="evtTime">
                {d.eventTime ? Utils.dateUtil.getTimeZone(d.eventTime, DATE_TIME_FORMATS.DATE_FORMAT) : '--'}
            </TableCell>
            <TableCell width="100px" key="user">
                {d.userId || '--'}
            </TableCell>
            <TableCell width="100px" key="application" className='word-break'>
                {d.applicationName || d.applicationKey || '--'}
            </TableCell>
            <TableCell width="100px" key="result">
                {
                    (d.isMasked || d.isAllowed)
                    ? <Typography variant="body2" style={{ color: d.isMasked ? '#0A84F7' : '#0F9956' }}>
                        {
                            d.isMasked ? MESSAGE_RESULT_TYPE.MASKED.LABEL : MESSAGE_RESULT_TYPE.ALLOWED.LABEL
                        }
                    </Typography>
                    : <Typography variant="body2" style={{ color: '#f50057' }}>{MESSAGE_RESULT_TYPE.DENIED.LABEL}</Typography>
                }
            </TableCell>
            <TableCell width="150px" key="sensitiveData"  style={{ borderRight: '1px solid rgba(224, 224, 224, 1)' }}> 
                <TraitChipList model={d}/>
            </TableCell>
        </TableRow>
    ])
  }
  render() {
    const {llmModel, pageChange, isLastRow} = this.props
    const { expandedRows } = this.props;
    const isExpanded = expandedRows.includes(llmModel[0]?.threadId);
    return (
    <TableRow className={`inner-table ${!isExpanded? "hide" : ""} ${isExpanded && isLastRow ? "audit-border-bottom" : "" }`}>
        <TableCell key="emptyCell" colSpan="7">
            <Table
                data={llmModel}
                getRowData={this.rows}
                isRowCustom={true}
                showContextMenu={false}
                onContextMenuSelection={this.handleContextMenuSelection}
                resizable={false}
                tableId="security_audit"
                hasElevation={false}
                pageChange={pageChange}
            />
        </TableCell>
    </TableRow>
    )
  }

}

const ExpandAuditsIcon = ({ width, height, fill, className }) => {
    return (
      <svg
        width={width}
        height={height}
        viewBox="0 0 15 15"
        fill={fill}
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        <rect width="15" height="15" rx="2" fill="#0A84F7" />
        <path
          d="M1.86558 4.37379C1.55933 4.68004 1.55933 5.17379 1.86558 5.48004L7.05933 10.6738C7.30308 10.9175 7.69683 10.9175 7.94058 10.6738L13.1343 5.48004C13.4406 5.17379 13.4406 4.68004 13.1343 4.37379C12.8281 4.06754 12.3343 4.06754 12.0281 4.37379L7.49683 8.89879L2.96558 4.36754C2.66558 4.06754 2.16558 4.06754 1.86558 4.37379Z"
          fill="white"
        />
      </svg>
    );
}

export default VSecurityAudits;