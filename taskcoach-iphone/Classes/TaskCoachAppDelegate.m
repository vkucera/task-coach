//
//  TaskCoachAppDelegate.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright Jérôme Laheurte 2009. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "PositionStore.h"
#import "CDDomainObject+Addons.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "i18n.h"
#import "CategoryViewController.h"
#import "CategoryTaskViewController.h"
#import "Migration.h"
#import "ReminderController.h"
#import "LogUtils.h"

NSManagedObjectContext *getManagedObjectContext(void)
{
	return ((TaskCoachAppDelegate *)([UIApplication sharedApplication].delegate)).managedObjectContext;
}

@implementation TaskCoachAppDelegate

@synthesize window;
@synthesize mainController;

- (void)applicationDidFinishLaunching:(UIApplication *)application
{
	// These lines are just there so that gettext can retrieve strings
	// in the NIB. Remember to add a line here each time a translatable
	// string appears in a NIB.
	
	// TaskDetailsControlleriPad
	_("Start date");
	_("Due date");
	_("Completion date");
	_("Reminder");
	_("Recurrence");
	_("Start tracking");
	_("Categories");
	_("Activity log");

	// TaskView
	_("Sync");

	// DatePickerView
	_("Save");
	_("Cancel");
	
	// MainWindow
	_("Categories");
	_("Sync");
	
	// MainWindow-iPad
	_("Categories");
	_("Sync");

	// TaskDetailsRecurrencePeriodPicker
	_("Save");
	_("Cancel");

#ifdef DEBUG
	LogSetLevel(LOGLEVEL_INFO);
#endif

	JLINFO("Started.");

	[window addSubview:mainController.view];
	[window makeKeyAndVisible];
}

/*
- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
	[self applicationDidFinishLaunching:application];

	[[ReminderController instance] check:launchOptions != nil];

	return YES;
}
*/

- (void)applicationDidBecomeActive:(UIApplication *)application
{
	[[ReminderController instance] unscheduleLocalNotifications];
	[[ReminderController instance] check:NO];
}

- (void)applicationWillResignActive:(UIApplication *)application
{
	[[ReminderController instance] scheduleLocalNotifications];

	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir withIntermediateDirectories:YES attributes:nil error:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store.v4"];
	[[PositionStore instance] save:path];
	
	[fileManager release];
	
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

- (void)application:(UIApplication *)application didReceiveLocalNotification:(UILocalNotification *)notification
{
	[[ReminderController instance] check:YES];
}

- (void)dealloc
{
    [managedObjectContext release];
    [managedObjectModel release];
    [persistentStoreCoordinator release];

	[mainController release];
    [window release];

    [super dealloc];
}

- (void)applicationWillTerminate:(UIApplication *)application
{
	if ([mainController respondsToSelector:@selector(willTerminate)])
		[mainController performSelector:@selector(willTerminate)];
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
	
	[fileManager release];
	
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
