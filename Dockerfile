# source docker: my custom build of python + uWSGI
FROM dellelce/uwsgi as build

# build wheels for pysam & pytabix
RUN apk add gcc binutils libc-dev linux-headers bzip2-dev make && \
    pip3 install wheel -U pip setuptools && \
    mkdir /wheel && \
    pip3 wheel -w /wheel pysam pytabix

# target environment
FROM dellelce/uwsgi as install

COPY --from=build /wheel /wheel

# install wheels and other dependencies
RUN pip3 install --no-cache -U pip setuptools pyvcf && \
    pip3 install --no-cache /wheel/* && \
    rm -rf /wheel

COPY src /src

# Todo:
#    complete review of python code
#    make this runnable: python code needs to be reviewed
#    convert php code to flask or install php/nginx/?
