from shoghlanah.models import *
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.template import RequestContext, Context
from django import template
from django.http import Http404
from forms import uploadProfilePicture
from forms import uploadCoverPicture
from django.http import HttpResponse,Http404
from shoghlanah.live_stream import add_action
from django.utils import formats, translation
from ShoghlanahProject import settings

from StringIO import StringIO
import pusher
import boto
from boto import *
import json
import os


def upload_page( request ):
    ctx = RequestContext( request, {
    'csrf_token': get_token( request ),
    } )
    return render_to_response( 'upload_page.html', ctx )


def upload_chunk(chunk,counter,mp):
    
    buffer = StringIO(chunk)
    # buffer.write(chunk)
    # buffer.seek(0)
    mp.upload_part_from_file(buffer,counter)
    buffer.close()
    
# This method is called in case of uploading on S3       
def upload_file(upload, filename, is_raw, user,mp):
        try:
            count = 0
            if is_raw:            
                    
                # File was uploaded via ajax, and is streaming in.
                chunk = upload.read(10485760)
                
                while len(chunk) > 0:
                    count += 1
                    upload_chunk(chunk, count, mp)
                    
                    chunk = upload.read(10485760)
            else:
                # File was uploaded via a POST, and is here.
                for chunk in upload.chunks():
                    count += 1
                    upload_chunk(chunk, count ,mp)
            return True
        except:
            return False

#This method is used on local upload            
def save_upload( uploaded, filename, raw_data, user ):
    """
    raw_data: if True, uploaded is an HttpRequest object with the file being
            the raw post data 
            if False, uploaded has been submitted via the basic form
            submission and is a regular Django UploadedFile in request.FILES
    """
    try:
        filename = filename.replace (" ", "_")
        filepath = '/'.join(['Gallery', user.username, filename])
        from io import FileIO, BufferedWriter
        with BufferedWriter( FileIO( '/'.join([settings.MEDIA_ROOT,filepath]), "wb" ) ) as dest:
        # if the "advanced" upload, read directly from the HTTP request 
        # with the Django 1.3 functionality
            if raw_data:
                foo = uploaded.read( 1024 )
                while foo:
                    dest.write( foo )
                    foo = uploaded.read( 1024 ) 
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks( ):
                    dest.write( c )
                # got through saving the upload, report success
            image = Photo()
            image.title=filename
            image.image=filepath
            image.owner=user
            image.save()
            add_action(actor=user, verb="upload_photo", action_object=user, description=image.image, target=user)
            return True
    except IOError:
    # could not open the file most likely
        pass
    return False

def ajax_upload( request ):
    if request.method == "POST":
        if request.is_ajax( ):
            
        # the file is stored raw in the request
            upload = request
            is_raw = True
            # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
            try:
                filename = request.GET[ 'qqfile' ]
            except KeyError: 
                return HttpResponseBadRequest( "AJAX request not valid" )
        # not an ajax upload, so it was the "basic" iframe version with submission via form
        else:
            
            is_raw = False
            if len( request.FILES ) == 1:
                # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
                # ID based on a random number, so it cannot be guessed here in the code.
                # Rather than editing Ajax Upload to pass the ID in the querystring,
                # observer that each upload is a separate request,
                # so FILES should only have one entry.
                # Thus, we can just grab the first (and only) value in the dict.
                upload = request.FILES.values( )[ 0 ]
            else:
                raise Http404( "Bad Upload" )
                filename = upload.name

        # save the file
        user = UserProfile.objects.get(id= request.user.id)
        # In case locally
        if settings.DEBUG:
            folder = '/'.join([settings.MEDIA_ROOT,'Gallery', user.username])
            if not os.path.isdir(folder):
                  os.makedirs(folder)
            filename = filename.replace (" ", "_")
            success = save_upload( upload, filename, is_raw, user )
        else:
            filename = filename.replace (" ", "_")
            
            # The path to save to the image
            folder = '/'.join([settings.MEDIA_ROOT+'Gallery', user.username, filename])
            filepath =  '/'.join(['Gallery', user.username, filename])
            # Initiate the connection with S3        
            c = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            s3 = c.lookup(settings.AWS_STORAGE_BUCKET_NAME)
            mp = s3.initiate_multipart_upload(folder)
            
            success = upload_file( upload, folder, is_raw, user,mp )
            if success:
                # for debug to check if the the file is uploaded
                mp.complete_upload()
                print 'after complete'
                image = Photo()
                image.title=filename
                image.image=filepath
                image.owner=user
                image.save()
                add_action(actor=user, verb="upload_photo", action_object=user, description=image.image, target=user)
            else:
                mp.cancel_upload()
        # let Ajax Upload know whether we saved it or not
        import json
        ret_json = { 'success': success, }
        return HttpResponse( json.dumps( ret_json ) )

def action_gallery(request, count):
    photos = Photo.objects.filter(owner__id=request.user.id).order_by('id')
    x=photos.reverse()[:int(count)]
    url_list=[u.image.url for u in x]
    url_list = url_list[0]
    requestuser = UserProfile.objects.get(username=request.user.username)
    try:
        url_list = url_list[0:url_list.index('?')]
    except:
        pass
    add_action(actor=requestuser, verb="upload_photo", action_object=requestuser, description=url_list, target=requestuser)
    return HttpResponse('')
