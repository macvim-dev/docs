"use strict";

var tagname = new URL(document.URL).searchParams.get('tag')
if (tagname && window.vimtags) {
    var redirectUrl = window.vimtags[tagname];
    if (redirectUrl) {
        window.location = redirectUrl;
    }
}
