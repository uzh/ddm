$(document).ready()
$('.inline-add-item-btn').click(function (event) {
	event.preventDefault();

	// Get prefix of inline forms
	let parent = $(this).parent();
	let first_input_element = parent.children('input').first();

	// Get the referencing form table
	let form_table = $(this).prev('table');

	// Get the 2 input elements before the table
	let mgmt_input_1 = form_table.prev('input')
	let mgmt_input_2 = mgmt_input_1.prev('input')

	// Copy these 2 elements
	let new_mgmt_input_1 = mgmt_input_1.clone()
	let new_mgmt_input_2 = mgmt_input_2.clone()

	// Get current running id
	let regexp = /^.+\-(.+)\-.*$/;
	let run_id = regexp.exec(new_mgmt_input_1.attr('name'))[1];
	run_id = Number(run_id) + 1

	// Increase number of total forms
	first_input_element.prop('value', Number(first_input_element.attr('value')) + 1);

	// Replace running ids in the two new management input elements
	function create_new_attr(element, attribute, new_id) {
		let regexp = /^(.+\-)(.+)(\-.*)$/;
		let current_attr = element.attr(attribute);
		let new_attr = current_attr.replace(regexp, ('$1' + new_id + '$3'));
		return new_attr;
	}
	new_mgmt_input_1.prop('id', create_new_attr(new_mgmt_input_1, 'id', run_id))
	new_mgmt_input_1.prop('name', create_new_attr(new_mgmt_input_1, 'name', run_id))

	new_mgmt_input_2.prop('id', create_new_attr(new_mgmt_input_2, 'id', run_id))
	new_mgmt_input_2.prop('name', create_new_attr(new_mgmt_input_2, 'name', run_id))

	// insert elements before table
	new_mgmt_input_1.insertBefore(form_table);
	new_mgmt_input_2.insertBefore(form_table);


	// Copy table row
	let table_row = form_table.find('tr').last();
	let new_table_row = table_row.clone();

	// Loop over inputs in new table row
	new_table_row.find( 'input' ).each(function() {
		let regexp = /^(.+\-)(.+)(\-.*)$/;
		let current_id = $( this ).attr('id')
		$( this ).prop('id', current_id.replace(regexp, '$1'+run_id+'$3'));

		let current_name = $( this ).attr('name');
		$( this ).prop('name', current_name.replace(regexp, '$1'+run_id+'$3'));

		$( this ).val([]);
	});

	new_table_row.insertAfter(table_row);
});


function changeDropup(elementId) {
	let dropupButton = document.getElementById(elementId);
	let dropupContent = dropupButton.nextElementSibling;
	if ( dropupContent.classList.contains('sq-dropup-show') ) {
		dropupContent.classList.remove('sq-dropup-show');
		dropupButton.firstElementChild.innerHTML = '&#9656;';
	} else {
		dropupContent.classList.add('sq-dropup-show');
		dropupButton.firstElementChild.innerHTML ='&#9652;';
	}
}

$(document).click(function(event) {
	if(!$(event.target).closest('#sq-dropup-content').length) {
		if($('#sq-dropup-content').hasClass('sq-dropup-show')) {
			$('#sq-dropup-content').removeClass('sq-dropup-show');
			$('#sq-dropup-button').find('span').html('&#9656;');
		}
	}
})
