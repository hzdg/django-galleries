function showGenericRelatedObjectLookupPopup(triggeringLink, ctArray)
{
    var realName = triggeringLink.id.replace(/^lookup_/, '');
    var name = id_to_windowname(realName);
    realName = realName.replace(/object_id/, 'content_type');
    var select = document.getElementById(realName);

    if (select.value === "") {
        alert("Select a content type first.");
        return false;
    }
    var selectedItem = select.item(select.selectedIndex).value;

    var href = triggeringLink.href.replace(/(\?|\#).*/,'../../../'+ctArray[selectedItem]);
    if (href.search(/\?/) >= 0) {
        href = href + '&_popup=1';
    } else {
        href = href + '?_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}
