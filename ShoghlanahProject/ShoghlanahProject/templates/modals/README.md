in this folder "modals" should be all the modals that we are going to use in our project

instead of having every html file jammed with a lot of modals, we can put those modals each in a separate html file in 'modals' folder name the file same as its ID and in the html file that needs that modal just include the file

for example:
{% include 'modals/invite-cont.html' %}
this is a modal with id="invite-cont" that is included in viewTask.html
