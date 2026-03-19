---
title: UK Parking Areas
date: 2019-10-28
authors: James Uther
---

I heard [Saul Griffith](https://medium.com/@saulgriffith) say recently that if you covered all the car parks in the USA with solar panels you would supply way more than the national energy requirements (I can\'t find the actual reference, but just go and watch his talks and read everything he\'s written).

I claimed this might translate to the UK. *But does it?*

The solar part is easy enough. If we electrify everything and want to remove carbon based generation, we need to build 300TWh of renewables. For the sake of argument let\'s do it all in solar (yes, i know, but ignore clouds and nights for now. It\'s a [spherical cow](https://en.wikipedia.org/wiki/Spherical_cow)).

Now according to [CAT](https://www.cat.org.uk/info-resources/free-information-service/energy/solar-photovoltaic/) to generate 800kWh (per year) we\'d need \~1kW of panels, which might be 8m², or 125kWh/m². so 300TWh / 125kWh = 24\*10⁸ m², or 2400 km²

Right. Does the UK have 2400 km² of parking?

Turns out that openstreetmap can give a (probably wrong) answer. Below I present a cleaned up route I hacked out to get there. The following politely elides the many, many detours and dead ends along the way.


            
    python3 -m venv e
    . e/bin/activate
    pip install geopandas descartes ipykernel matplotlib jupyter
    python -m ipykernel install --user --name=e
    # get the great-britain-latest.osm.bpf file 
    # from https://download.geofabrik.de/europe/great-britain.html

    brew install osmosis geos
    osmosis --read-pbf great-britain-latest.osm.pbf \
      --tf accept-ways amenity=parking --tf reject-relations \
      --used-node --way-key-value keyValueList="amenity.parking" \
      --write-xml gb-parking.osm

    npm install -g osmtogeojson
    osmtogeojson gb-parking.osm > gb-parking.json

    jupyter notebook
        

And then in the notebook:


          
    import geopandas
    import matplotlib
    p = geopandas.read_file("gb-parking.json")
    p = p[p['id'].str[:4] == 'way/'] # remove stuff we don't need

And wait another while for my poor laptop to warm the room. No one ever accused python of being fast.

Now, check we have something. This should draw all the parking areas in the UK.


            
    _ = p.plot(figsize=(4, 8))
        

\[there should be an image here but it didn\'t survive a move. will try and reproduce one day\]

So something, but it\'s a bit hard to see so let\'s try plotting where they are with big blobs


            
    p = p.rename(columns={'geometry': 'borders'}).set_geometry('borders')
    p['centroids'] = p.centroid
    p = p.set_geometry('centroids')
    p.plot(figsize=(8,16))
    p = p.set_geometry('borders') # reset geometry
       

\[ditto about the image\]

Now the geometry we have doesn\'t give us the correct units (we want m²) so change to something else, then add all the areas up and convert to km²


            
    cart = p.to_crs({'init': 'epsg:3395'})
    sum(cart.area) / 10**6
          

gives


            
    679.3396674106002
          

Tada! 🎉. So apparently no! At least from the crowdsourced OSM data. We\'d have to use more than just car parks 😢.
