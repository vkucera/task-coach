//
//  GUIDState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "TaskFileNameState.h"
#import "CDFile.h"
#import "Configuration.h"
#import "CDDomainObject.h"

@implementation GUIDState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[GUIDState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[self startWithFormat:"s" count:NOCOUNT];
}

- (void)onNewObject:(NSArray *)value
{
	NSString *guid = [value objectAtIndex:0];

	NSLog(@"Got GUID: %@", guid);

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"guid == %@", guid]];
	NSError *error;
	NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	CDFile *theFile;

	if (results)
	{
		switch ([results count])
		{
			case 0:
			{
				// Create it.
				theFile = (CDFile *)[NSEntityDescription insertNewObjectForEntityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()];
				theFile.guid = guid;

				// As a special case, if some objects are not associated with any file, they become associated with this
				// one and marked new (if not deleted). This happens when the user has never synced, or when he has
				// created objects after deleting all files. In either case, either all objects are concerned or none.
				
				[request setEntity:[NSEntityDescription entityForName:@"CDDomainObject" inManagedObjectContext:getManagedObjectContext()]];
				[request setPredicate:[NSPredicate predicateWithFormat:@"file == NULL"]];
				results = [getManagedObjectContext() executeFetchRequest:request error:&error];
				
				if (results)
				{
					for (CDDomainObject *object in results)
						object.file = theFile;
				}
				else
				{
					NSLog(@"Could not fetch objects: %@", [error localizedDescription]);
				}
				
				break;
			}
			case 1:
				theFile = [results objectAtIndex:0];
				break;
			default:
				assert(0);
		}

		[Configuration configuration].cdCurrentFile = theFile;
		[[Configuration configuration] save];
	}
	else
	{
		NSLog(@"Could not fetch files: %@", [error localizedDescription]);
		[self cancel];
		return;
	}
	
	[request release];
	
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
	myController.state = [TaskFileNameState stateWithNetwork:myNetwork controller:myController];
}

- (void)onFinished
{
}

@end
