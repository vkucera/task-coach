//
//  GUIDState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "TaskFileNameState.h"

@implementation GUIDState

- (void)activated
{
	[myNetwork expect:4];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[GUIDState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[fileId release];

	[super dealloc];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)onFile:(NSDictionary *)dict
{
	fileId = [[dict objectForKey:@"id"] retain];
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	switch (state)
	{
		case 0:
			state = 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case 1:
		{
			NSString *guid = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
			
			NSLog(@"Got GUID: %@", guid);
			
			// Look for file...
			Statement *req = [[Database connection] statementWithSQL:@"SELECT id FROM TaskCoachFile WHERE guid=?"];
			[req bindString:guid atIndex:1];
			[req execWithTarget:self action:@selector(onFile:)];
			
			[[[Database connection] statementWithSQL:@"UPDATE TaskCoachFile SET visible=0"] exec];
			
			if (!fileId)
			{
				// Create a new one.
				
				Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO TaskCoachFile (guid) VALUES (?)"];
				[req bindString:guid atIndex:1];
				[req exec];
				fileId = [[NSNumber numberWithInt:[[Database connection] lastRowID]] retain];
				
				// As a special case, if some objects are not associated with any file, they become associated with this
				// one and marked new (if not deleted). This happens when the user has never synced, or when he has
				// created objects after deleting all files. In either case, either all objects are concerned or none.
				
				[[[Database connection] statementWithSQL:@"DELETE FROM Task WHERE fileId IS NULL AND status=3"] exec];
				[[[Database connection] statementWithSQL:@"DELETE FROM Category WHERE fileId IS NULL AND status=3"] exec];
				[[[Database connection] statementWithSQL:@"UPDATE Task SET status=1 WHERE fileId IS NULL"] exec];
				[[[Database connection] statementWithSQL:@"UPDATE Category SET status=1 WHERE fileId IS NULL"] exec];
				[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE Task SET fileId=%@ WHERE fileId IS NULL", fileId]] exec];
				[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE Category SET fileId=%@ WHERE fileId IS NULL", fileId]] exec];
			}
			
			[guid release];
			
			// Make this file the current one.
			[Database connection].currentFile = fileId;
			[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE TaskCoachFile SET visible=1 WHERE id=%@", fileId]] exec];
			
			[network appendInteger:1];
			controller.state = [TaskFileNameState stateWithNetwork:network controller:controller];

			break;
		}
	}
}

@end
