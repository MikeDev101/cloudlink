from montydb import set_storage, MontyClient


set_storage(
    # general settings
    
    repository="./db/repo",  # dir path for database to live on disk, default is {cwd}
    storage="flatfile",     # storage name, default "flatfile"
    mongo_version="4.0",    # try matching behavior with this mongodb version
    use_bson=False,         # default None, and will import pymongo's bson if None or True

    # any other kwargs are storage engine settings.
    
    cache_modified=10,       # the only setting that flat-file have
)
