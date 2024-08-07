import {createMuiTheme} from '@material-ui/core/styles';

const theme = createMuiTheme({
	/*typography: {
		subtitle1: {
			fontWeight: '300'
		},
		fontWeight: '400',
		fontFamily: 'Heebo,' +
			'Arial,sans-serif'
	},*/
	palette: {
		// type: 'light',
		primary: {
			light: '#0A84F7',
			main: '#0A84F7',
			dark: '#0A84F7',
			contrastText: '#fff'
		}
	},
	overrides: {
	    MuiCssBaseline: {
            '@global': {
                body: {
                    backgroundColor: '#F4F9FC !important'
                },
                '.loader-container': {
                    backgroundColor: '#F4F9FC !important'
                },
				'.border-bottom': {
					borderBottom: '1px solid #E0E0E0'
				},
				'.border-right': {
					borderRight: '1px solid #E0E0E0'
				},
				'.list-item-text-selected': {
					color: '#2D4ADA'
				}
            }
        },
		MuiAppBar: {
			colorPrimary: {
				backgroundColor: '#FFF !important',
				color: '#1d1d1e'
			}
		},
		MuiDrawer: {
			paper: {
				backgroundColor: '#FFF !important',
				color: '#1c1c1c'
			},

		},
		MuiListItem: {
		    root: {
				'&.active-list-item': {
					color: '#2D4ADA',
					backgroundColor: '#F4F9FC'
				  },
				'&.list-item:hover': {
					backgroundColor: '#CDD9E2 !important'
				},
				'& .list-item-icon': {
					color: '#777',

					'& svg': {
						fill: '#777'
					}
				},
				'&.navlist-element:hover': {
					backgroundColor: '#CDD9E2 !important',
					color: '#fff'
				},
				'&.active-list-item .list-item-icon svg': {
					color: '#2D4ADA',
					fill: '#2D4ADA'
				},
				'&.active-list-parent': {
					'&.menu-expanded': {
						backgroundColor: '#D8E4EE !important'
					},
				},
				'&.active-list-item:hover': {
					backgroundColor: '#2D4ADA !important',
					color: '#ffffff',

					'& .list-item-icon svg': {
						color: '#ffffff',
						fill: '#ffffff'
					}
				},
				'&.active-list-item:hover svg': {
					color: '#fff'
				},
				'&$selected': {
					backgroundColor: '#f4f9fc'
				  },
				  '&$selected:hover': {
					backgroundColor: '#EAF3FA'
				  }

			}
		},
		MuiSvgIcon: {
			root: {
				'&.info-color': {
					color: '#FF4D01 !important'
				}
			},
			colorPrimary: {
				color: '#0A84F7 !important'
			}
		},
		MuiIconButton: {
			root: {
				'&$disabled': {
					color: '#c4c4c4 !important'
				}
			},
			colorPrimary: {
				color: '#0A84F7 !important',
			}
		},
		MuiCheckbox: {
			root: {
				'&$disabled': {
					color: '#c4c4c4 !important'
				}
			},
			colorPrimary: {
				color: '#757575 !important',
				'&$checked': {
					color: '#0A84F7 !important'
				}
			}
		},
		MuiButton: {
			label: {
				fontWeight: '400'
			},
			containedPrimary: {
				backgroundColor: '#2D4ADA',
				'&:hover': {
					backgroundColor: '#405ADD'
				}
			},
			textPrimary: {
				color: '#0A84F7 !important',
			},
			containedSecondary: {
				backgroundColor: '#FC5439 !important',
			},
			textSecondary: {
				color: '#FC5439 !important',
			},
			contained: {
				'&.Mui-disabled': {
					color: 'rgba(0, 0, 0, 0.38) !important',
					boxShadow: 'none !important',
					backgroundColor: 'rgba(0, 0, 0, 0.12) !important'
				}
			},
			outlinedPrimary: {
				border: '1px solid #dddddd !important'
			},
			root: {
				// fontFamily: 'Heebo,Arial,sans-serif !important'
			}
		},
		MuiFilledInput: {
			inputMultiline: {
				padding: '27px 12px 10px'
			},
			root: {
				backgroundColor: 'rgba(0,0,0,0.04)',
				'&:hover': {
					backgroundColor: 'rgba(0,0,0,0.08)'
				}
			}
		},
		MuiOutlinedInput: {
			root: {
				borderRadius: 0,
				'&.Mui-disabled': {
					background: '#f1f1f1',
					opacity: '0.8',
					color: 'rgba(0, 0, 0, 0.78)'
				},
				backgroundColor: '#fff !important'
			},
			input: {
				paddingTop: '8px !important',
				paddingBottom: '8px !important',
				minHeight: '20px',
				'&.Mui-disabled': {
					cursor: 'not-allowed'
				},
				backgroundColor: '#fff !important',

			},
			multiline:{
				padding: '14px'
			}
		},
		MuiFormLabel: {
			root: {
				color: '#787878'
			},
			asterisk: {
				color: '#FC5439'
			}
		},
		MuiInputBase: {
			input: {
				color: 'black !important',
				fontSize: '14px',
				border: '1px solid transparent !important'
			}
		},
		MuiTableCell: {
			head: {
				lineHeight: 'normal'
			}
		},
		MuiAutocomplete: {
			paper: {
				fontSize: '14px'
			}
		},
		MuiFormControlLabel: {
			label: {
				fontSize: '14px'
			},
			root: {
				color: '#787878',
				marginRight: '4px'
			}
		},
		MuiBadge: {
			// colorPrimary: {
			// 	backgroundColor: '#FF4D01 !important'
			// }
		},
		MuiChip: {
			label: {
				fontSize: '12px'
			},
			root: {
				'&.selected-chip': {
					backgroundColor: '#2D4ADA !important'
				}
			}
		},
		MuiAutocomplete: {
			inputRoot: {
				paddingTop: '0 !important',
				paddingBottom: '0 !important'
			},
			tag: {
				fontSize: '14px'
			}
		},
		MuiMenuItem: {
			root: {
				fontSize: '14px'
			}
		},
		MuiFormHelperText:{
			contained:{
				marginLeft: '0px'
			}
		},
		MuiTab: {
			root: {
				'&$selected': {
					color: '#2D4ADA !important'
				}
			}
		},
		MuiTabs: {
			indicator: {
				backgroundColor: '#2D4ADA !important'
			}
		},
		MuiToggleButton: {
			root: {
				'&$selected': {
					backgroundColor: '#2D4ADA'
				},
				'&$selected&:hover': {
					backgroundColor: '#2D4ADA'
				}
			}
		},
		MuiSwitch: {
			colorPrimary: {
				// color: '#172538 !important',
				'&$checked': {
					color: '#2D4ADA !important'
				},
				'&$checked&$disabled': {
					color: '#ABB7F0 !important'
				},
				'&$checked&$disabled + $track': {
					backgroundColor: '#2D4ADA !important'
				}
			}
		},
		MuiTabScrollButton: {
			root: {
				'&$disabled': {
					MuiTabScrollButton: {
						root: {
							opacity: '0.5 !important'
						}
					}
				}
			}
		}
	}
});

export default theme;