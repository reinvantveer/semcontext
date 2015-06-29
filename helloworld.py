"""A simple webapp2 server."""
import sys
sys.path.insert(0, 'lib')

import cgi
import webapp2
import rdflib
from rdflib import Graph
import pyparsing

MAIN_PAGE_HTML = """\
<!doctype html>
<html>
	<body>
	<script src="js/jquery/jquery-1.11.0.min.js"></script>
	<script src="js/arbor/arbor.js"></script>

	<script>
		(function($){

		  var Renderer = function(canvas){
			var canvas = $(canvas).get(0)
			var ctx = canvas.getContext("2d");
			var particleSystem

			var that = {
			  init:function(system){
				//
				// the particle system will call the init function once, right before the
				// first frame is to be drawn. it's a good place to set up the canvas and
				// to pass the canvas size to the particle system
				//
				// save a reference to the particle system for use in the .redraw() loop
				particleSystem = system

				// inform the system of the screen dimensions so it can map coords for us.
				// if the canvas is ever resized, screenSize should be called again with
				// the new dimensions
				particleSystem.screenSize(canvas.width, canvas.height)
				particleSystem.screenPadding(80) // leave an extra 80px of whitespace per side
				
				// set up some event handlers to allow for node-dragging
				that.initMouseHandling()
			  },
			  
			  redraw:function(){
				//
				// redraw will be called repeatedly during the run whenever the node positions
				// change. the new positions for the nodes can be accessed by looking at the
				// .p attribute of a given node. however the p.x & p.y values are in the coordinates
				// of the particle system rather than the screen. you can either map them to
				// the screen yourself, or use the convenience iterators .eachNode (and .eachEdge)
				// which allow you to step through the actual node objects but also pass an
				// x,y point in the screen's coordinate system
				//
				ctx.fillStyle = "white";
				ctx.fillRect(0,0, canvas.width, canvas.height);
				
				particleSystem.eachEdge(function(edge, pt1, pt2){
				  // edge: {source:Node, target:Node, length:#, data:{}}
				  // pt1: {x:#, y:#} source position in screen coords
				  // pt2: {x:#, y:#} target position in screen coords

				  // draw a line from pt1 to pt2
				  ctx.strokeStyle = "rgba(0,0,0, .333)";
				  ctx.lineWidth = 1;
				  ctx.beginPath();
				  ctx.moveTo(pt1.x, pt1.y);
				  ctx.lineTo(pt2.x, pt2.y);
				  ctx.stroke();
				  
				  ctx.fillStyle = "black";
				  ctx.font = 'italic 13px sans-serif';
				  ctx.fillText (edge.data.name, (pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2);
				})

				particleSystem.eachNode(function(node, pt){
				  // node: {mass:#, p:{x,y}, name:"", data:{}};
				  // pt: {x:#, y:#} node position in screen coords;

				  // draw a rectangle centered at pt
				  var w = 10;
				  ctx.fillStyle = (node.data.alone) ? "orange" : "black";
				  ctx.fillRect(pt.x-w/2, pt.y-w/2, w,w);
				  ctx.fillStyle = "black";
				  ctx.font = 'italic 13px sans-serif';
				  ctx.fillText (node.name, pt.x+8, pt.y+8);
				})
			  },
			  
			  initMouseHandling:function(){
				// no-nonsense drag and drop (thanks springy.js)
				var dragged = null;

				// set up a handler object that will initially listen for mousedowns then
				// for moves and mouseups while dragging
				var handler = {
				  clicked:function(e){
					var pos = $(canvas).offset();
					_mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top);
					dragged = particleSystem.nearest(_mouseP);

					if (dragged && dragged.node !== null){
					  // while we're dragging, don't let physics move the node
					  dragged.node.fixed = true;
					}

					$(canvas).bind('mousemove', handler.dragged);
					$(window).bind('mouseup', handler.dropped);

					return false;
				  },
				  dragged:function(e){
					var pos = $(canvas).offset();
					var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top);

					if (dragged && dragged.node !== null){
					  var p = particleSystem.fromScreen(s);
					  dragged.node.p = p;
					}

					return false;
				  },

				  dropped:function(e){
					if (dragged===null || dragged.node===undefined) return;
					if (dragged.node !== null) dragged.node.fixed = false;
					dragged.node.tempMass = 1000;
					dragged = null;
					$(canvas).unbind('mousemove', handler.dragged);
					$(window).unbind('mouseup', handler.dropped);
					_mouseP = null;
					return false;
				  }
				}
				
				// start listening
				$(canvas).mousedown(handler.clicked);

			  },
			  
			}
			return that
		  }

		  $(document).ready(function(){
			var sys = arbor.ParticleSystem(1000, 600, 0.5) // create the system with sensible repulsion/stiffness/friction
			sys.parameters({gravity:true}) // use center-gravity to make the graph settle nicely (ymmv)
			sys.renderer = Renderer("#viewport") // our newly created renderer will have its .init() method called shortly by sys...

			/* add some nodes to the graph and watch it go...
			sys.addNode('a', {mass: 3, link: '/dinges'})
			sys.addEdge('a','b', 'van a naar b')
			sys.addEdge('a','c', 'van a naar c')
			sys.addEdge('a','d', 'van a naar d')
			sys.addEdge('a','e', 'van a naar e')
			sys.addNode('f', {alone:true, mass:.25})
			*/

			var theUI = {
				nodes:{
					"arbor.js":{color:"red", shape:"dot", alpha:1}, 
					demos:{color:"purple", shape:"dot", alpha:1}, 
					halfviz:{color:"green", alpha:0, link:'/halfviz'},
					atlas:{color:"yellow", alpha:0, link:'/atlas'},
					echolalia:{color:"blue", alpha:0, link:'/echolalia'},
					docs:{color:"black", shape:"dot", alpha:1}, 
					reference:{color:"blue", alpha:0, link:'#reference'},
					introduction:{color:"red", alpha:0, link:'#introduction'},

					code:{color:"black", shape:"dot", alpha:1},
					github:{color:"grey", alpha:0, link:'https://github.com/samizdatco/arbor'},
					".zip":{color:"red", alpha:0, link:'/js/dist/arbor-v0.92.zip'},
					".tar.gz":{color:"green", alpha:0, link:'/js/dist/arbor-v0.92.tar.gz'}
				},
				edges:{
					"arbor.js":{
					  demos:{length:.8},
					  docs:{length:.8},
					  code:{length:.8}
					},
					demos:{halfviz:{},
						   atlas:{},
						   echolalia:{}
					},
					docs:{reference:{},
						  introduction:{}
					},
					code:{".zip":{},
						  ".tar.gz":{},
						  "github":{}
					}
				}
			}
			sys.graft(theUI)
			
		  })

		})(this.jQuery)
		
		function visualizeGraph()
		{
			$.ajax({
				url:"/parse",
				type:'POST',
				data: 'content=' + $('#content').val(),
				success: function(data){ 
					alert(data);
				}
			});
		}
	</script>
	<h1>The incredible chronological consistency checker!</h1>
	<h2>RDF</h2>
	<p>This simple application uses the <a href="http://www.w3.org/RDF/">Resource Description Framework (RDF)</a> and <a href="http://en.wikipedia.org/wiki/SPARQL">SPARQL</a> to detect inconsistencies in simple RDF facts commonly known as <a href="http://en.wikipedia.org/wiki/Resource_Description_Framework#Overview">triples</a>. The example below shows a circular argument of several triples, where the whole represents something like the <a href="http://en.wikipedia.org/wiki/Penrose_stairs">Penrose stairs</a> immortalized in <a href="http://www.mcescher.nl/galerij/erkenning-succes/klimmen-en-dalen/">Escher's famous never-ending staircase</a> - an impossible spatial configuration</p>
	<p>Where detection using standard database and SQL of such an inconsistency would be a <a href="http://stackoverflow.com/questions/1757260/simplest-way-to-do-a-recursive-self-join-in-sql-server">complex operation</a>, with linked data this operation is very simple.</p> 
	<h2>SPARQL</h2>
	<p>The SPARQL query looks a bit different from standard SQL, but is not hard to understand:</p>
	PREFIX time:&lthttp://www.w3.org/2006/time#&gt <br>
	SELECT DISTINCT ?startcontext ?endcontext<br>
	WHERE {<br>
		?startcontext time:after+ ?endcontext .<br>
		?endcontext time:after ?startcontext. <br>
	} ORDER BY ?startcontext<br>
	
	<p>The plus-sign is the only 'extra' operator needed for the recursivity in the query and indicates a <a href="http://www.w3.org/TR/sparql11-property-paths/">'property path'</a> operator, meaning that the query will try following the same predicate <i>time:after</i> once; twice; as many times as it can from fact to fact, before checking whether the 'endcontext' doubles back to the 'startcontext' to form a circular argument.</p>
	<p>Try it yourself with the example <a href="http://www.google.nl/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&ved=0CDgQFjAB&url=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FTurtle_(syntax)&ei=tcA5U-2xFoXt0gXKgoHwBg&usg=AFQjCNGNS_ZDcryLexf8rsfgQG-dYZbbpA&sig2=ycEST949IBN9JjGr-hs5fg&bvm=bv.63808443,d.d2k">rdf/turtle</a> snippet below...</p>
    <div style="width:auto ;">
		<div style="float:right; width:50%;"><canvas id="viewport" width="400" height="300"></canvas></div>
		<div style="float:left; width:50%;"><form action="/sign" method="post">
		  <div><textarea name="content" id="content" rows="10" cols="60">
@prefix time: <http://www.w3.org/2006/time#> . 
"a" time:after "b" .
"b" time:after "c" .
"c" time:after "d" .
"d" time:after "e" .
"e" time:after "a" .
		</textarea></div>
		  <div><input type="submit" value="Parse rdf/turtle"></div>
		  <div><input type="button" value="Visualize" onclick="visualizeGraph();"></div>
		</form></div>
	</div>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/HTML'
		
	self.response.write('<p>Using <a href="http://www.rdflib.net">RDFlib</a> version ' + rdflib.__version__ + '</p>')
	self.response.write(MAIN_PAGE_HTML)

class CheckConsistency(webapp2.RequestHandler):
	def post(self):
		#try:
		#self.response.write(cgi.escape(self.request.get('content')))
		g = Graph()
		g.parse(data=self.request.get('content'), format='turtle')
		self.response.write('<h2>Succesfully parsed!</h2>')
		qres = g.query(
			"""
			PREFIX time:<http://www.w3.org/2006/time#> 
			SELECT DISTINCT ?startcontext ?endcontext
			WHERE {
				?startcontext time:after+ ?endcontext .
				?endcontext time:after ?startcontext. 
			} ORDER BY ?startcontext """)
		if qres.__len__() != 0:
			self.response.write('<p>A chronological circularity has been detected:</p>')
			for row in qres:
				self.response.write('<p> %s is younger than %s ' % row + '</p>')
		else:
			self.response.write('<p>No chronological circularity has been detected</p>')
		#self.response.write(cgi.escape(g.serialize(format='xml')))
		#except Exception:
			#self.response.write('<br/><p>An error occurred parsing the input<p><br/>')
			#pass
class ParseInput(webapp2.RequestHandler):
	def post(self):
		g = Graph()
		g.parse(data=self.request.get('content'), format='turtle')
		qres = g.query(
			"""
			PREFIX time:<http://www.w3.org/2006/time#> 
			SELECT DISTINCT ?startcontext ?endcontext
			WHERE {
				?startcontext time:after+ ?endcontext .
				?endcontext time:after ?startcontext. 
			} ORDER BY ?startcontext """)
		if qres.__len__() != 0:
			self.response.write('<p>A chronological circularity has been detected:</p>')
			for row in qres:
				self.response.write('<p> %s is younger than %s ' % row + '</p>')
		else:
			self.response.write('<p>No chronological circularity has been detected</p>')

application = webapp2.WSGIApplication([
    ('/', MainPage),
	('/sign', CheckConsistency),
	('/parse', ParseInput)
], debug=True)