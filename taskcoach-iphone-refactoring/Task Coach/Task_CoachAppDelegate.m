//
//  Task_CoachAppDelegate.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Task_CoachAppDelegate.h"
#import "Migration.h"
#import "Configuration.h"
#import "CDDomainObject.h"
#import "CDFile.h"
#import "CDList.h"

NSManagedObjectContext *getManagedObjectContext(void)
{
	return ((Task_CoachAppDelegate *)([UIApplication sharedApplication].delegate)).managedObjectContext;
}

NSPersistentStoreCoordinator *getPersistentStoreCoordinator(void)
{
    return ((Task_CoachAppDelegate *)([UIApplication sharedApplication].delegate)).persistentStoreCoordinator;
}

@implementation Task_CoachAppDelegate


@synthesize window=_window;

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
    // Override point for customization after application launch.
    [self.window makeKeyAndVisible];
    return YES;
}

- (void)applicationWillResignActive:(UIApplication *)application
{
    /*
     Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
     Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
     */

	NSError *error;
	
	if (managedObjectContext != nil)
	{
        if ([managedObjectContext hasChanges] && ![managedObjectContext save:&error])
		{
			NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
			exit(-1);  // Fail
        } 
    }
}

- (void)applicationDidEnterBackground:(UIApplication *)application
{
    /*
     Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
     If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
     */
}

- (void)applicationWillEnterForeground:(UIApplication *)application
{
    /*
     Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
     */
}

- (void)applicationDidBecomeActive:(UIApplication *)application
{
    /*
     Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
     */
}

- (void)applicationWillTerminate:(UIApplication *)application
{
    /*
     Called when the application is about to terminate.
     Save data if appropriate.
     See also applicationDidEnterBackground:.
     */
}

- (void)dealloc
{
    [managedObjectContext release];
    [managedObjectModel release];
    [persistentStoreCoordinator release];
    
    [_window release];
    [super dealloc];
}

#pragma mark -
#pragma mark Core Data stack

/**
 Returns the managed object context for the application.
 If the context doesn't already exist, it is created and bound to the persistent store coordinator for the application.
 */
- (NSManagedObjectContext *) managedObjectContext
{
    if (managedObjectContext != nil)
	{
        return managedObjectContext;
    }
	
    NSPersistentStoreCoordinator *coordinator = [self persistentStoreCoordinator];
    if (coordinator != nil)
	{
        managedObjectContext = [[NSManagedObjectContext alloc] init];
        [managedObjectContext setPersistentStoreCoordinator: coordinator];
    }
	
	// We don't use undo, so save memory
	[[managedObjectContext undoManager] disableUndoRegistration];
    
    return managedObjectContext;
}


/**
 Returns the managed object model for the application.
 If the model doesn't already exist, it is created by merging all of the models found in the application bundle.
 */
- (NSManagedObjectModel *)managedObjectModel
{
    if (managedObjectModel != nil)
	{
        return managedObjectModel;
    }
	
	NSString *path = [[NSBundle mainBundle] pathForResource:@"TaskCoachCD" ofType:@"momd"];
    NSURL *momURL = [NSURL fileURLWithPath:path];
    managedObjectModel = [[NSManagedObjectModel alloc] initWithContentsOfURL:momURL];
	
    return managedObjectModel;
}


/**
 Returns the persistent store coordinator for the application.
 If the coordinator doesn't already exist, it is created and the application's store added to it.
 */
- (NSPersistentStoreCoordinator *)persistentStoreCoordinator
{
    if (persistentStoreCoordinator != nil)
	{
        return persistentStoreCoordinator;
    }
    
	NSString *path = [[self applicationDocumentsDirectory] stringByAppendingPathComponent: @"TaskCoachCD.sqlite"];
    NSURL *storeUrl = [NSURL fileURLWithPath: path];
    
	NSError *error;
    persistentStoreCoordinator = [[NSPersistentStoreCoordinator alloc] initWithManagedObjectModel: [self managedObjectModel]];
	NSDictionary *options = [NSDictionary dictionaryWithObjectsAndKeys:
							 [NSNumber numberWithBool:YES], NSMigratePersistentStoresAutomaticallyOption,
							 [NSNumber numberWithBool:YES], NSInferMappingModelAutomaticallyOption, nil];
    if (![persistentStoreCoordinator addPersistentStoreWithType:NSSQLiteStoreType configuration:nil URL:storeUrl options:options error:&error])
	{
		NSLog(@"Could not create store: %@", [error localizedDescription]);
    }    
	
	// Migrate old sqlite database
	
	NSString* filename = @"taskcoach.db";
	NSArray *documentPaths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
	NSString *documentsDir = [documentPaths objectAtIndex:0];
	NSString *databasePath = [documentsDir stringByAppendingPathComponent:filename];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if ([fileManager fileExistsAtPath:databasePath])
	{
		@try
		{
			migrateOldDatabase(databasePath);
			
			NSError *error;
			if (![fileManager removeItemAtPath:databasePath error:&error])
			{
				@throw [NSException exceptionWithName:@"DatabaseError" reason:[error localizedDescription] userInfo:nil];
			}
		}
		@catch (NSException * e)
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error"
															message:[NSString stringWithFormat:@"Error migrating data: %@", [e reason]]
														   delegate:self
												  cancelButtonTitle:@"OK"
												  otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
		
	}

    // When upgrading from Task Coach v3.x, replace existing files with lists.
    
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir withIntermediateDirectories:YES attributes:nil error:nil];
	}
	
	path = [cachesDir stringByAppendingPathComponent:@"positions.store.v4"];

    if ([fileManager fileExistsAtPath:path])
    {
        NSError *error;

        // First convert files to lists
        NSFetchRequest *req = [[NSFetchRequest alloc] init];
        [req setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
        NSArray *files = [getManagedObjectContext() executeFetchRequest:req error:&error];
        [req release];

        if (!files)
        {
            NSLog(@"Could not fetch files: %@", [error localizedDescription]);
        }
        else
        {
            CDList *defaultList = nil;

            for (CDFile *aFile in files)
            {
                NSLog(@"Creating list for file %@", aFile.name);

                CDList *lst = [NSEntityDescription insertNewObjectForEntityForName:@"CDList" inManagedObjectContext:getManagedObjectContext()];
                lst.file = aFile;
                lst.name = [aFile.name stringByDeletingPathExtension];

                if (!defaultList)
                    defaultList = lst;
                
                req = [[NSFetchRequest alloc] init];
                [req setEntity:[NSEntityDescription entityForName:@"CDDomainObject" inManagedObjectContext:getManagedObjectContext()]];
                [req setPredicate:[NSPredicate predicateWithFormat:@"file=%@", aFile]];
                NSArray *objects = [getManagedObjectContext() executeFetchRequest:req error:&error];
                [req release];
                
                if (!objects)
                {
                    NSLog(@"Could not fetch objects: %@", [error localizedDescription]);
                }
                else
                {
                    for (CDDomainObject *obj in objects)
                    {
                        NSLog(@"Migrating object \"%@\" to list \"%@\"", obj.name, lst.name);
                        obj.list = lst;
                    }
                }
            }

            if (![getManagedObjectContext() save:&error])
            {
                NSLog(@"Could not save: %@", [error localizedDescription]);
            }

            if (defaultList)
            {
                [Configuration instance].currentList = defaultList;
                [[Configuration instance] save];
            }
        }

        [fileManager removeItemAtPath:path error:&error];
    }

    /*
	// Update date status for all objects
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d", STATUS_DELETED]];
	
	NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
	if (tasks)
	{
		for (CDTask *task in tasks)
			[task computeDateStatus];
		
		if (![getManagedObjectContext() save:&error])
		{
			JLERROR("Error saving: %s", [[error localizedDescription] UTF8String]);
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not save tasks" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
	else
	{
		JLERROR("Error fetching: %s", [[error localizedDescription] UTF8String]);
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not load tasks" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
    
	[request release];
     */
    
    return persistentStoreCoordinator;
}


#pragma mark -
#pragma mark Application's documents directory

/**
 Returns the path to the application's documents directory.
 */
- (NSString *)applicationDocumentsDirectory
{
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *basePath = ([paths count] > 0) ? [paths objectAtIndex:0] : nil;
    return basePath;
}

@end
