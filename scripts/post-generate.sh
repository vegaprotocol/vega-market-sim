#!/usr/bin/env bash

generated_dir="${GENERATED_DIR:?}"

for x in \
	data_node/api/v1 \
	data_node/api/v2 \
	vega/api/v1 \
	vega/checkpoint/v1 \
	vega/commands/v1 \
	vega/events/v1 \
	vega/data/v1 \
	vega/snapshot/v1 \
	vega/wallet/v1
do
	# from . import XX as XX
	pb_py="$(find "$generated_dir/$x/" -maxdepth 1 -name '*_pb2.py' -o -name '*_pb2_grpc.py' -o -type d | sort | tail -n +2)"
	(
		echo "$pb_py" | while read -r pb ; do
			if test -f "$pb" ; then
				imp="$(basename "${pb//.py/}")"
				echo "from . import $imp as ${imp/_pb2/}"
			elif test -d "$pb" ; then
				imp="$(basename "$pb")"
				echo "from . import $imp"
			else
				echo "# Ignoring: $pb"
			fi
		done
		echo
	) > "$generated_dir/$x/__init__.py"

	# __all__ = [...]
	(
		echo "__all__ = ["
		echo "$pb_py" | while read -r pb ; do
			if test -f "$pb" ; then
				imp="$(basename "${pb//.py/}")"
				echo "    \"${imp/_pb2/}\","
			elif test -d "$pb" ; then
				imp="$(basename "$pb")"
				echo "    \"$imp\","
			else
				echo "# Ignoring: $pb"
			fi
		done
		echo "]"
	) >> "$generated_dir/$x/__init__.py"
done

for x in \
	vega/api \
	vega/checkpoint \
	vega/commands \
	vega/events \
	vega/data \
	vega/snapshot \
	vega/wallet
do
	cat >"$generated_dir/$x/__init__.py" <<EOF
from . import v1

__all__ = ["v1"]
EOF
done

for x in \
	data_node/api
do
	cat >"$generated_dir/$x/__init__.py" <<EOF
from . import v1, v2

__all__ = ["v1", "v2"]
EOF
done

cat >"$generated_dir/data_node/__init__.py" <<EOF
from . import api

__all__ = ["api"]
EOF

python3 generate_vega_init.py >"$generated_dir/vega/__init__.py"

cat >"$generated_dir/__init__.py" <<EOF
from . import data_node, vega

__all__ = ["data_node", "vega"]
EOF

for x in \
	. \
	data_node/api \
	vega/api \
	vega/checkpoint \
	vega/commands \
	vega/events \
	vega/data \
	vega/snapshot \
	vega/wallet
do
	touch "$generated_dir/$x/__init__.py"
done

find "$generated_dir/vega" -maxdepth 1 -name '*.py' -print0 | xargs -0r sed --in-place -r \
	-e 's#^from vega import ([a-z_]*)_pb2 as #from . import \1_pb2 as #' \
	-e 's#^from vega.commands.v1 import#from .commands.v1 import#' \
	-e 's#^from vega.events.v1 import#from .events.v1 import#' \
	-e 's#^from vega.data.v1 import#from .data.v1 import#' \
	-e 's#^from vega.snapshot.v1 import#from .snapshot.v1 import#' \
	-e 's#^from vega.wallet.v1 import#from .wallet.v1 import#' \
	-e 's#^from vega.checkpoint.v1 import#from .checkpoint.v1 import#' \
	-e 's#^import ([a-z_]*)_pb2 as #from . import \1_pb2 as #'

find "$generated_dir/vega/api" -maxdepth 1 -name '*.py' -print0 | xargs -0r sed --in-place -r \
	-e 's#^from vega import ([a-z_]*)_pb2 as#from .. import \1_pb2 as#' \
	-e 's#^from vega.api import #from . import #' \
	-e 's#^from vega.commands.v1 import#from ..commands.v1 import#' \
	-e 's#^from vega.events.v1 import#from ..events.v1 import#' \
	-e 's#^from vega.data.v1 import#from ..data.v1 import#' \
	-e 's#^from vega.snapshot.v1 import#from ..snapshot.v1 import#' \
	-e 's#^from vega.wallet.v1 import#from ..wallet.v1 import#' \
	-e 's#^from vega.checkpoint.v1 import#from ..checkpoint.v1 import#' \
	-e 's#^import ([a-z_]*)_pb2 as #from ... import \1_pb2 as #'

find \
	"$generated_dir/vega/api/v1" \
	"$generated_dir/vega/checkpoint/v1" \
	"$generated_dir/vega/commands/v1" \
	"$generated_dir/vega/events/v1" \
	"$generated_dir/vega/data/v1" \
	"$generated_dir/vega/snapshot/v1" \
	"$generated_dir/vega/wallet/v1" \
	-maxdepth 1 -name '*.py' -print0 | xargs -0r sed --in-place -r \
	-e 's#^from vega import ([a-z_]*)_pb2 as#from ... import \1_pb2 as#' \
	-e 's#^from vega.(api.v1|commands.v1|events.v1|data.v1|snapshot.v1|wallet.v1|checkpoint.v1|github.com.mwitkow.go_proto_validators) import #from ...\1 import #' \
	-e 's#^import ([a-z_]*_pb2) as #from ... import \1 as #'

find \
	"$generated_dir/data_node/api/v1" \
	-maxdepth 1 -name '*.py' -print0 | xargs -0r sed --in-place -r \
	-e 's#^from vega import ([a-z_]*)_pb2 as#from ....vega import \1_pb2 as#' \
	-e 's#^from vega.(api.v1|commands.v1|events.v1|data.v1|snapshot.v1|wallet.v1|checkpoint.v1|github.com.mwitkow.go_proto_validators) import #from ....vega.\1 import #' \
	-e 's#^from data_node.(api.v1) import #from ...\1 import #'

find \
	"$generated_dir/data_node/api/v2" \
	-maxdepth 1 -name '*.py' -print0 | xargs -0r sed --in-place -r \
	-e 's#^from vega import ([a-z_]*)_pb2 as#from ....vega import \1_pb2 as#' \
	-e 's#^from vega.(api.v1|commands.v1|events.v1|data.v1|snapshot.v1|wallet.v1|checkpoint.v1|github.com.mwitkow.go_proto_validators) import #from ....vega.\1 import #' \
	-e 's#^from data_node.(api.v2) import #from ...\1 import #'

find "$generated_dir" -name '*.py' -print0 | xargs -0r sed --in-place -re 's#[ \t]+$##'