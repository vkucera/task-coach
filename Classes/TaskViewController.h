//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface TaskViewController : UITableViewController
{
	NSString *title;
}

- initWithTitle:(NSString *)title;

@end
