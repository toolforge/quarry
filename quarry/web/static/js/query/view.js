$( () => {
	function htmlEscape( str ) {
		return String( str )
			.replace( /&/g, '&amp;' )
			.replace( /"/g, '&quot;' )
			.replace( /'/g, '&#39;' )
			.replace( /</g, '&lt;' )
			.replace( />/g, '&gt;' );
	}

	CodeMirror.extendMode( 'sql', { electricChars: ')' } );
	function makeEditor() {
		return CodeMirror.fromTextArea( $( '#code' )[ 0 ], {
			mode: 'text/x-mariadb',
			theme: 'monokai',
			readOnly: !vars.can_edit,
			matchBrackets: true,
			lineNumbers: true
		} );
	}

	let editor = makeEditor();
	$( '#query-description' ).autosize();
	$.ajax( {
		url: '/api/dbs',
		success: function ( data ) {
			addAutocompleteDB( document.getElementById( 'query-db' ), data.dbs );
		}
	} );

	function addAutocompleteDB( input_elem, options ) {
		/* Autocomplete an input element from the given array
		adapted from https://www.w3schools.com/howto/howto_js_autocomplete.asp */
		let currentFocus;
		input_elem.addEventListener( 'input', function () {
			const val = this.value;
			closeAllLists();
			if ( !val ) {
				return false;
			}
			currentFocus = -1;

			// eslint-disable-next-line no-jquery/variable-pattern,no-jquery/no-constructor-attributes
			const list_elem = $( '<div>', {
				id: this.id + '-autocomplete-list',
				class: 'autocomplete-items'
			} );
			list_elem.appendTo( input_elem.parentElement );
			for ( let i = 0; i < options.length; i++ ) {
				/* check if the item starts with the same letters as the text field value: */
				if ( options[ i ].slice( 0, val.length ).toUpperCase() === val.toUpperCase() ) {
					$( '<div><strong>' + options[ i ].slice( 0, val.length ) + options[ i ].slice( val.length ) + '</strong><input type="hidden" value="' + options[ i ] + '">' )
						.on( {
							click: function () {
								input_elem.value = this.getElementsByTagName( 'input' )[ 0 ].value;
								closeAllLists();
							}
						} )
						.appendTo( list_elem );
					console.log( 'Got a matching element to', val, '  -> ', options[ i ] );
				}
			}
		} );

		input_elem.addEventListener( 'keydown', function ( e ) {
			let list_elem = document.getElementById( this.id + '-autocomplete-list' );
			if ( list_elem ) {
				list_elem = list_elem.getElementsByTagName( 'div' );
			}
			if ( e.keyCode === 40 ) {
				/* If the arrow DOWN key is pressed,
				increase the currentFocus variable: */
				currentFocus++;
				/* and and make the current item more visible: */
				addActive( list_elem );
			} else if ( e.keyCode === 38 ) {
				/* If the arrow UP key is pressed,
				decrease the currentFocus variable: */
				currentFocus--;
				/* and and make the current item more visible: */
				addActive( list_elem );
			} else if ( e.keyCode === 13 ) {
				/* If the ENTER key is pressed, prevent the form from being submitted, */
				e.preventDefault();
				if ( currentFocus > -1 ) {
				/* and simulate a click on the "active" item: */
					if ( list_elem ) {
						list_elem[ currentFocus ].click();
					}
				}
			} else if ( e.keyCode === 9 ) {
				/* close dropdown on tab press */
				if ( currentFocus > -1 ) {
				/* if focus was moved before tab press, use it */
					if ( list_elem ) {
						list_elem[ currentFocus ].click();
					}
				} else {
					closeAllLists();
				}
			}
		} );

		function addActive( list_elem ) {
			/* tag the next item in the list as active by adding the autocomplete-active class */
			if ( !list_elem ) {
				return false;
			}
			removeActive( list_elem );
			if ( currentFocus >= list_elem.length ) {
				currentFocus = 0;
			}
			if ( currentFocus < 0 ) {
				currentFocus = ( list_elem.length - 1 );
			}
			list_elem[ currentFocus ].classList.add( 'autocomplete-active' );
		}

		function removeActive( list_elem ) {
			/* clear all active items from the list */
			for ( let i = 0; i < list_elem.length; i++ ) {
				list_elem[ i ].classList.remove( 'autocomplete-active' );
			}
		}

		function closeAllLists( not_to_close ) {
			/* close all autocomplete lists in the document, except the one passed as an argument: */
			const autocomplete_items = document.getElementsByClassName( 'autocomplete-items' );
			for ( let i = 0; i < autocomplete_items.length; i++ ) {
				if ( not_to_close !== autocomplete_items[ i ] && not_to_close !== input_elem ) {
					autocomplete_items[ i ].parentNode.removeChild( autocomplete_items[ i ] );
				}
			}
		}

		/* clear all autocomplete lists if there's a click anywhere */
		document.addEventListener( 'click', ( e ) => {
			closeAllLists( e.target );
		} );
	}

	if ( vars.can_edit ) {
		$( '#title' ).on( 'blur', () => {
			const title = $( '#title' ).val();
			$.post( '/api/query/meta', {
				query_id: vars.query_id,
				title: title
			} ).done( ( /* data */ ) => {
				document.title = ( title || 'Untitled query #' + vars.query_id ) + ' - Quarry';
			} );
		} );
	}

	$( '#togglehl' ).on( 'click', () => {
		if ( editor === null ) {
			editor = makeEditor();
		} else {
			editor.toTextArea();
			editor = null;
		}
	} );

	$( '#un-star-query' ).on( 'click', () => {
		$.post( '/api/query/unstar', {
			query_id: vars.query_id
		} ).done( ( /* data */ ) => {
			$( '#content' ).removeClass( 'starred' );
		} );
	} );

	$( '#star-query' ).on( 'click', () => {
		$.post( '/api/query/star', {
			query_id: vars.query_id
		} ).done( ( /* data */ ) => {
			$( '#content' ).addClass( 'starred' );
		} );
	} );

	$( '#query-description' ).on( 'blur', () => {
		$.post( '/api/query/meta', {
			query_id: vars.query_id,
			description: $( '#query-description' ).val()
		} ).done( () => {
			// Uh, do nothing?
		} );
	} );

	$( '#toggle-publish' ).on( 'click', () => {
		$.post( '/api/query/meta', {
			query_id: vars.query_id,
			published: vars.published ? 0 : 1
		} ).done( ( /* data */ ) => {
			// eslint-disable-next-line no-jquery/no-class-state
			$( '#content' ).toggleClass( 'published' );
			vars.published = !vars.published;
		} );
	} );

	$( '#stop-code' ).on( 'click', () => {
		updateFavicon( 'default' );

		$.post( '/api/query/stop', {
			query_database: $( '#query-db' ).val(),
			qrun_id: vars.qrun_id
		} )
			.done( () => {
				checkStatus( vars.qrun_id, false );
			} )
			.fail( ( resp ) => {
				alert( resp.responseText );
			} );
	} );

	$( '#run-code' ).on( 'click', () => {
		updateFavicon( 'running' );

		$.post( '/api/query/run', {
			text: editor !== null ? editor.getValue() : $( '#code' ).val(),
			query_database: $( '#query-db' ).val(),
			query_id: vars.query_id
		} )
			.done( ( data ) => {
				vars.output_url = data.output_url;
				$( '#query-progress' ).show();
				$( '#query-result-error' ).hide();
				$( '#query-result-success' ).hide();
				clearTimeout( window.lastStatusCheck );
				checkStatus( data.qrun_id, false );
				vars.qrun_id = data.qrun_id;
			} )
			.fail( ( resp ) => {
				alert( resp.responseText );
			} );
		return false;
	} );

	function checkStatus( qrun_id, silent ) {
		const url = '/run/' + qrun_id + '/status';
		$.get( url ).done( ( data ) => {
			$( '#query-status' ).html( 'Query status: <strong>' + data.status + '</strong>' );
			$( '#query-result' ).html(
				nunjucks.render( 'query-status.html', data )
			);
			if ( data.status === 'complete' ) {
				if ( data.extra.resultsets.length ) {
					populateResults( qrun_id, 0, data.extra.resultsets.length );
				} else {
					$( '#query-result' ).prepend( '<p id="emptyresultsetmsg">This query returned no results.</p>' );
				}

				const runningdate = new Date( data.timestamp * 1000 );
				// Compatibility handling, old requests do not have the execution time stored.
				let headertext = 'Executed on ';
				if ( data.extra.runningtime ) {
					headertext = 'Executed in ' + data.extra.runningtime + ' seconds as of ';
				}
				$( '#query-result' ).prepend(
					'<p id="queryheadermsg">' + headertext + '<span title="' + runningdate.toString() + '">' +
					runningdate.toUTCString().replace( 'GMT', 'UTC' ) + '</span>.</p>'
				);

				if ( !silent && vars.preferences.use_notifications ) {
					const title = $( '#title' ).val() ? '"' + $( '#title' ).val() + '"' : 'Untitled query #' + vars.query_id;
					sendNotification( title + ' execution has been completed' );
				}

				updateFavicon( 'default' );
			} else if ( data.status === 'queued' || data.status === 'running' ) {
				window.lastStatusCheck = setTimeout( () => {
					checkStatus( qrun_id, false );
				}, 5000 );
				updateFavicon( 'running' );
			}

			/* separating this section from the above, similar, section as this has to
			do with the status button where the above has to do with the status results.
			They already diverge a little in purpose, could diverge more later */
			if ( data.status === 'running' ) {
				document.getElementById( 'stop-code' ).style.visibility = 'visible';
			} else {
				document.getElementById( 'stop-code' ).style.visibility = 'hidden';
			}
			$( '#show-explain' ).off().on( 'click', () => {
				$.get( '/explain/' + $( '#query-db' ).val() + '/' + data.extra.connection_id ).done( ( explain ) => {
					let $table = $( '#explain-results-table' );
					if ( !$table.length ) {
						$table = $( '<table>' ).attr( {
							class: 'table',
							id: 'explain-results-table'
						} );

						$( '#query-result-container' ).append( $table );
					}

					populateTable( $table, explain );
				} );
			} );
		} );
	}

	function populateTable( $table, data ) {
		const columns = [];
		// eslint-disable-next-line no-jquery/no-each-util
		$.each( data.headers, ( i, header ) => {
			columns.push( {
				title: htmlEscape( header ),
				render: function ( item /* , type, row */ ) {
					if ( typeof item === 'string' ) {
						return htmlEscape( item );
					} else {
						return item;
					}
				}
			} );
		} );

		$table.dataTable( {
			data: data.rows,
			columns: columns,
			scrollX: true,
			pagingType: 'simple_numbers',
			paging: data.rows.length > 100,
			pageLength: 100,
			lengthMenu: [ 10, 25, 50, 100, 200, 250, 500 ],
			deferRender: true,
			order: [],
			destroy: true
		} );

		// Ugly hack to ensure that table rows actually show
		// up. Otherwise they don't until you do a resize.
		// Browser and DOM bugs are the best.
		$table.DataTable().draw();
	}

	function slugifyTitle() {
		return ( $( '#title' ).val() || 'untitled' )
			.toLowerCase()
			.split( /[\t !"#$%&'()*-/<=>?@[\\\]^_`{|},.]+/g )
			.filter( ( word ) => word )
			.join( '-' );
	}

	function populateResults( qrun_id, resultset_id, till ) {
		const url = '/run/' + qrun_id + '/output/' + resultset_id + '/json';
		$.get( url ).done( ( data ) => {
			// eslint-disable-next-line no-jquery/variable-pattern
			const tableContainer = $( nunjucks.render( 'query-resultset.html', {
					only_resultset: resultset_id === till - 1,
					resultset_number: resultset_id + 1,
					rowcount: data.rows.length,
					resultset_id: resultset_id,
					run_id: qrun_id,
					query_id: vars.query_id,
					slugify_title: slugifyTitle()
				} ) ),
				$table = tableContainer.find( 'table' );
			$( '#query-result' ).append( tableContainer );

			populateTable( $table, data );

			if ( resultset_id < till - 1 ) {
				populateResults( qrun_id, resultset_id + 1, till );
			}
		} );
	}

	function sendNotification( text ) {
		if ( Notification.permission === 'granted' ) {
			// eslint-disable-next-line no-new
			new Notification( 'Quarry', {
				icon: '/static/img/quarry-logo-icon.svg',
				body: text
			} );
		} else {
			console.log( 'Can\'t send notification, permission value is set to ' + Notification.permission );
			$.get( '/api/preferences/set/use_notifications/null' );
		}
	}

	function updateFavicon( state ) {
		const favicon = document.querySelector( "link[rel='icon']" );
		if ( state === 'running' ) {
			favicon.href = '/static/img/favicon-running.png';
		} else {
			favicon.href = '/static/img/favicon.png';
		}
	}

	if ( vars.qrun_id ) {
		checkStatus( vars.qrun_id, true );
	} else {
		$( '#query-status' ).text( 'This query has never yet been executed' );
	}
} );
