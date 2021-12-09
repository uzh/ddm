$('.surquest-oq-textarea, .surquest-oq-textline').on('keyup change input', function(event) {

	if ($elem.attr('chars') != 'text') {
		let $elem = $(this),
	    value = $elem.val(),
	    regReplace,
	    filter = $elem.attr('chars');

	    regReplace = new RegExp(filter, 'ig');
	    $elem.val(value.replace(regReplace, ''));
	}
});


var coll = document.getElementsByClassName('sq-collapsible');
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener('click', function() {
    this.classList.toggle('active');
    let content = this.nextElementSibling;
    if (content.style.display === 'block') {
      content.style.display = 'none';
    } else {
      content.style.display = 'block';
    }
  });
}
