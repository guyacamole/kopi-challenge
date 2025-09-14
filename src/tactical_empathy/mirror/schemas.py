from pydantic import BaseModel, Field
from typing import Dict, List
import uuid
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    """Schema for a message."""
    content: str = Field(..., description="The content of the message", example="Hello, how are you?")--------------------

  27 |     # RUN python manage.py migrate

  28 |     

  29 | >>> RUN python manage.py collectstatic --noinput

  30 |     

  31 |     EXPOSE 8000

--------------------

failed to solve: process "/bin/sh -c python manage.py collectstatic --noinput" did not complete successfully: exit code: 1

668  /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

github.com/moby/buildkit/executor/runcexecutor.exitError

	/root/build-deb/engine/vendor/github.com/moby/buildkit/executor/runcexecutor/executor.go:391

github.com/moby/buildkit/executor/runcexecutor.(*runcExecutor).Run

	/root/build-deb/engine/vendor/github.com/moby/buildkit/executor/runcexecutor/executor.go:339

github.com/moby/buildkit/solver/llbsolver/ops.(*ExecOp).Exec

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/llbsolver/ops/exec.go:492

github.com/moby/buildkit/solver.(*sharedOp).Exec.func2

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/jobs.go:1120

github.com/moby/buildkit/util/flightcontrol.(*call[...]).run

	/root/build-deb/engine/vendor/github.com/moby/buildkit/util/flightcontrol/flightcontrol.go:122

sync.(*Once).doSlow

	/usr/local/go/src/sync/once.go:78

sync.(*Once).Do

	/usr/local/go/src/sync/once.go:69

runtime.goexit

	/usr/local/go/src/runtime/asm_arm64.s:1223



610991 v0.25.0 /usr/libexec/docker/cli-plugins/docker-buildx bake --file - --progress rawjson --metadata-file /tmp/compose-build-metadataFile-2142086426.json --allow fs.read=/home/guyacamole/docker/kopi-challenge

google.golang.org/grpc.(*ClientConn).Invoke

	google.golang.org/grpc@v1.72.2/call.go:35

github.com/moby/buildkit/api/services/control.(*controlClient).Solve

	github.com/moby/buildkit@v0.23.0/api/services/control/control_grpc.pb.go:88

github.com/moby/buildkit/client.(*Client).solve.func2

	github.com/moby/buildkit@v0.23.0/client/solve.go:268

golang.org/x/sync/errgroup.(*Group).add.func1

	golang.org/x/sync@v0.14.0/errgroup/errgroup.go:130

runtime.goexit

	runtime/asm_arm64.s:1223



668  /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

github.com/moby/buildkit/solver.(*edge).execOp

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/edge.go:963

github.com/moby/buildkit/solver/internal/pipe.NewWithFunction[...].func2

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/internal/pipe/pipe.go:78

runtime.goexit

	/usr/local/go/src/runtime/asm_arm64.s:1223



610991 v0.25.0 /usr/libexec/docker/cli-plugins/docker-buildx bake --file - --progress rawjson --metadata-file /tmp/compose-build-metadataFile-2142086426.json --allow fs.read=/home/guyacamole/docker/kopi-challenge

github.com/moby/buildkit/client.(*Client).solve.func2

	github.com/moby/buildkit@v0.23.0/client/solve.go:285

golang.org/x/sync/errgroup.(*Group).add.func1

	golang.org/x/sync@v0.14.0/errgroup/errgroup.go:130



668  /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

github.com/moby/buildkit/solver/llbsolver/ops.(*ExecOp).Exec

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/llbsolver/ops/exec.go:513

github.com/moby/buildkit/solver.(*sharedOp).Exec.func2

	/root/build-deb/engine/vendor/github.com/moby/buildkit/solver/jobs.go:1120



class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: uuid.UUID = Field(..., description="The conversation this message belongs to")
    role_name: str = Field(..., description="The role of the message sender", example="user")


class MessageResponse(BaseModel):
    """Schema for a message response."""
    id: uuid.UUID = Field(..., description="Unique identifier for the message")
    content: str = Field(..., description="The content of the message", example="Hello, how are you?")
    role_name: str = Field(..., description="The role of the message sender", example="user")
    conversation_id: uuid.UUID = Field(..., description="The conversation this message belongs to")
    created_at: datetime = Field(..., description="When the message was created")

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for list of messages response."""
    messages: List[MessageResponse] = Field(..., description="List of messages")


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, description="The content of the message")
    role_name: Optional[str] = Field(None, description="The role of the message sender")
    conversation_id: Optional[uuid.UUID] = Field(None, description="The conversation this message belongs to")


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    topic: str = Field(..., description="The topic of the conversation", max_length=255, example="Climate Change")
    bot_stance: str = Field(..., description="The bot's stance on the topic", max_length=255, example="Pro-environmental action")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    id: uuid.UUID
    topic: Optional[str] = Field(None, description="The topic of the conversation", max_length=255)
    bot_stance: Optional[str] = Field(None, description="The bot's stance on the topic", max_length=255)


class DebateContext(ConversationCreate):
  """Context model for debate conversations."""
  last_user_message: str
  conversation_history: list[Dict[str, str]] = []


class DebateCreate(BaseModel):
  """Schema for creating a chat."""
  user_message: str
  conversation_id: Optional[uuid.UUID] = None


class Debate(DebateCreate):
    """Schema for a chat."""
    messages: List[MessageResponse] = Field(..., description="List of messages in the debate")
    conversation_id: uuid.UUID = Field(..., description="The conversation this debate belongs to")


class DebateResponse(BaseModel):
    """Schema for a debate response."""
    conversation_id: uuid.UUID = Field(..., description="The conversation this debate belongs to")
    messages: List[MessageResponse] = Field(..., description="List of messages in the debate")
    user_message: str = Field(..., description="The user's message", example="I think climate change is serious")

    class Config:
        from_attributes = True


class DebateGet(BaseModel):
    """Schema for a debate get."""
    max_messages: int = Field(..., description="Maximum number of messages to retrieve", example=20)
    conversation_id: Optional[uuid.UUID] = Field(None, description="The conversation ID to get debate for")
  
class ConversationResponse(BaseModel):
    """Schema for a single conversation response."""
    id: uuid.UUID = Field(..., description="Unique identifier for the conversation")
    topic: str = Field(..., description="The topic of the conversation", example="Climate Change")
    bot_stance: str = Field(..., description="The bot's stance on the topic", example="Pro-environmental action")
    created_at: datetime = Field(..., description="When the conversation was created")
    updated_at: datetime = Field(..., description="When the conversation was last updated")
    is_active: bool = Field(..., description="Whether the conversation is active", example=True)

    class Config:
        from_attributes = True # Helps Pydantic work with Django models


class ConversationListResponse(BaseModel):
    """Schema for list of conversations response."""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message describing what went wrong", example="Invalid input data")


class SuccessMessage(BaseModel):
    """Schema for success message responses."""
    message: str = Field(..., description="Success message", example="Operation completed successfully")