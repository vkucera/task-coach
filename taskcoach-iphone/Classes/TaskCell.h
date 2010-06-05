//
//  TaskCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class CDTask;
@class CheckView;

@interface TaskCell : UITableViewCell
{
	NSManagedObjectID *ID;

	CheckView *leftImage;
	UILabel *titleLabel;
	
	id target;
	SEL action;
	
	BOOL isTapping;
}

@property (nonatomic, retain) NSManagedObjectID *ID;
@property (nonatomic, retain) IBOutlet CheckView *leftImage;
@property (nonatomic, retain) IBOutlet UILabel *titleLabel;

- (void)setTask:(CDTask *)task target:(id)target action:(SEL)action;

@end
