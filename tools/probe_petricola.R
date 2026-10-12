# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 500ft
# Original compatibility harness. Loaded upstream source is unchanged and external.
# This program is distributed without any warranty. See PETRICOLA_PROBE_LICENSE.md.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 3)
upstream <- normalizePath(args[1])
target_csv <- normalizePath(args[2])
output <- normalizePath(args[3], mustWork=FALSE)
dir.create(output, recursive=TRUE, showWarnings=FALSE)
setwd(output)
library(sf)
library(magrittr)
library(jsonlite)

capture <- function(expr) {
  tryCatch(list(status="returned", value=eval.parent(substitute(expr))),
           error=function(e) list(status="error", message=conditionMessage(e),
                                  call=paste(deparse(conditionCall(e)),collapse=" ")))
}
record <- list(runtime=R.version.string, sf=as.character(packageVersion("sf")),
               libraries=as.list(sf_extSoftVersion()),
               scope="Unmodified upstream helper and selected input read; synthetic service adapter. No ORS route or population computation.")
# Guard against unintentionally progressing to the original parallel driver on a fuller runtime.
stopifnot(!requireNamespace("rgeoboundaries", quietly=TRUE))
# Full original driver stops at its first unavailable dependency, before input/parallel work.
record$driver <- capture(source(file.path(upstream,"src/2_healthcare_access/vector_analysis/isochrones_main.R"),local=new.env()))
source(file.path(upstream,"src/2_healthcare_access/vector_analysis/1.1_isochrones_local.R"))
rows <- read.csv(target_csv)
points <- st_as_sf(rows,coords=c("longitude_deg","latitude_deg"),crs=4326)
record$without_backend_package <- capture(getIsochrones(points[1,],600,"driving-car","normal"))

# The preparation script writes health_facilities; the vector driver requests all.
dir.create("data/download",recursive=TRUE,showWarnings=FALSE)
st_write(points, "data/download/health_facilities.gpkg",layer="health_facilities",quiet=TRUE)
scope <- "all"
exprs <- parse(file.path(upstream,"src/2_healthcare_access/vector_analysis/isochrones_main.R"))
read_expr <- Filter(function(e) is.call(e) && identical(e[[1]],as.name("<-")) &&
                    identical(e[[2]],as.name("health_facilities")), as.list(exprs))
stopifnot(length(read_expr)==1)
record$original_input_read <- capture(eval(read_expr[[1]]))
record$available_layers <- st_layers("data/download/health_facilities.gpkg")$name
record$input_read_expression <- paste(deparse(read_expr[[1]]),collapse=" ")

# Explicit test double records calls; it never claims to route or generate a real isochrone.
observed <- list()
mode <- "ok"
ors_isochrones <- function(locations,range,profile,output) {
  observed[[length(observed)+1]] <<- list(locations=unname(locations),range=range,
        profile=profile,output=output,url=getOption("openrouteservice.url"))
  if (mode == "backend_error") stop("SYNTHETIC_ADAPTER: ORS unavailable")
  result <- st_sf(value=range,geometry=st_sfc(st_point(c(0,0)),crs=4326))
  if (mode == "geom_column") {
    names(result)[names(result)=="geometry"] <- "geom"
    st_geometry(result) <- "geom"
  }
  result
}
record$adapter_wgs84 <- capture({x <- getIsochrones(points[1,],600,"driving-car","normal");list(rows=nrow(x),columns=names(x),crs=st_crs(x)$epsg)})
record$adapter_wgs84_calls <- observed
observed <- list()
record$adapter_projected <- capture({x <- getIsochrones(st_transform(points[1,],32736),600,"driving-car","normal");list(rows=nrow(x),columns=names(x))})
record$adapter_projected_calls <- observed
mode <- "backend_error"
record$adapter_backend_failure <- capture(getIsochrones(points[1,],600,"driving-car","normal"))
mode <- "geom_column"
record$adapter_geometry_name <- capture(getIsochrones(points[1,],600,"driving-car","normal"))
mode <- "ok"
observed <- list()
record$empty_source <- capture({x <- getIsochrones(points[FALSE,],600,"driving-car","normal"); list(rows=nrow(x))})
record$empty_source_adapter_calls <- observed
# Strip accidental returned sf objects to keep failure logs compact and explicit.
write_json(record,"probe.json",pretty=TRUE,auto_unbox=TRUE,null="null",digits=16)
stopifnot(record$driver$status=="error",record$original_input_read$status=="error",
          record$adapter_wgs84$status=="returned",record$adapter_projected$status=="returned",
          record$adapter_backend_failure$status=="error")
cat("Compatibility probe completed; missing dependencies and adapters remain explicit.\n")
